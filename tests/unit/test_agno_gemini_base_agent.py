import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

from finance_assistant.application.handlers.telegram_handlers import build_start_message, markdown_to_telegram_html
from finance_assistant.infrastructure.agents.speech_to_text_agent import SpeechToTextAgent
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.add_expense_tool import add_expense
from finance_assistant.infrastructure.agents.base_agent import BaseAgent
from finance_assistant.infrastructure.agents.response_agent import FinanceAgent
from finance_assistant.infrastructure.config import settings as settings_module
from finance_assistant.infrastructure.config.settings import settings


def test_google_environment_settings_are_exposed_in_settings_surface(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("GOOGLE_PROJECT_ID", "test-project-id")

    importlib.reload(settings_module)

    assert settings_module.settings.google_client_id == "test-client-id"
    assert settings_module.settings.google_client_secret == "test-client-secret"
    assert settings_module.settings.google_project_id == "test-project-id"


# def test_base_agent_selects_gemini_flash_lite_model(monkeypatch):
#     monkeypatch.setattr(settings, "gemini_api_key", "test-key", raising=False)

#     base = BaseAgent()

#     assert base.model.id == "gemini-2.5-flash-lite"
#     assert base.model.api_key == "test-key"


def test_gemini_response_agent_can_wrap_agent_run(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key", raising=False)

    response_agent = FinanceAgent(instructions="You answer finance questions.")

    assert response_agent.agent is not None
    assert response_agent.agent.instructions == "You answer finance questions."


# def test_markdown_to_telegram_html_converts_common_markdown_to_html():
#     html = markdown_to_telegram_html("Hello **world** and <tag>")

#     assert "<p>Hello <strong>world</strong> and &lt;tag&gt;</p>" in html

def test_markdown_to_telegram_html_converts_to_bold():
    html = markdown_to_telegram_html("Hello **world**")

    assert "Hello <b>world</b>" in html

def test_markdown_to_telegram_html_converts_to_italic():
    html = markdown_to_telegram_html("Hello *world*")

    assert "Hello <i>world</i>" in html

def test_markdown_to_telegram_html_remove_hashtags():
    html = markdown_to_telegram_html("Hello #world")

    assert "Hello world" in html

def test_markdown_to_telegram_html_remove_multiple_hashtags():
    html = markdown_to_telegram_html("Hello ###world ##universe")

    assert "Hello world universe" in html

def test_build_start_message_includes_invoice_registration_guidance():
    message = build_start_message(123456789)

    assert "@kassiodev" in message
    assert "id do telegram" in message.lower()
    assert "e-mail" in message.lower()
    assert "Google Sheets" in message


def test_markdown_to_telegram_html_convert_bullet_points():
    html = markdown_to_telegram_html("* Vodafone *(Comunicação)*: **€13.45**")

    assert " • Vodafone <i>(Comunicação)</i>: <b>€13.45</b>" in html


def test_build_instructions_include_spreadsheet_id_and_range():
    from finance_assistant.application.handlers import telegram_handlers as handlers

    prompt = handlers.build_instructions("sheet-id", "'Recorrentes'!A1:E50")

    assert "sheet-id" in prompt
    assert "'Recorrentes'!A1:E50" in prompt


def test_base_agent_create_agent_accepts_spreadsheet_range_override(monkeypatch):
    import finance_assistant.infrastructure.agents.base_agent as base_agent_module

    captured = {}

    class DummyGoogleSheetsTools:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    class DummyAgent:
        def __init__(self, tools=None, model=None, instructions="", **kwargs):
            self.tools = tools
            self.model = model
            self.instructions = instructions
            self.kwargs = kwargs

    monkeypatch.setattr(base_agent_module, "GoogleSheetsTools", DummyGoogleSheetsTools)
    monkeypatch.setattr(base_agent_module, "Agent", DummyAgent)

    base = BaseAgent.__new__(BaseAgent)
    base.model = object()

    agent = base._create_agent("You answer finance questions.", spreadsheet_range="'Sumário'!B27:F42")

    assert captured["spreadsheet_range"] == "'Sumário'!B27:F42"
    assert agent.tools[0] is not None
    assert agent.tools[1].name == "get_last_expense"
    assert agent.tools[2].name == "add_expense"
    assert agent.tools[3].name == "validate_expense_row"


def test_get_last_expense_reads_the_last_non_empty_sheet_row(monkeypatch):
    from finance_assistant.infrastructure.agents.get_last_expense_tool import get_last_expense

    captured = {}

    class DummyGet:
        def execute(self):
            return {"values": [["date", "amount"], ["2026-09-14", "10.25"], []]}

    class DummyValues:
        def get(self, spreadsheetId, range):
            captured["spreadsheetId"] = spreadsheetId
            captured["range"] = range
            return DummyGet()

    class DummySheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: DummyValues())

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_last_expense_tool._get_sheets_service",
        lambda: DummySheets(),
    )
    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_last_expense_tool.TelegramAdapterService",
        lambda: SimpleNamespace(resolve_spreadsheet_id=lambda telegram_user_id: "sheet-id"),
    )

    message = get_last_expense.entrypoint(telegram_user_id=123)

    assert message == "Last expense: 2026-09-14 | 10.25"
    assert captured == {"spreadsheetId": "sheet-id", "range": "Despesas!B:F"}


def test_validate_expense_row_confirms_the_last_expense_values(monkeypatch):
    from finance_assistant.infrastructure.agents.validate_expense_row_tool import validate_expense_row

    class DummyGet:
        def execute(self):
            return {"values": [["🤖", "14/09/2026", "10.25", "coffee", "food"]]}

    class DummyValues:
        def get(self, spreadsheetId, range):
            assert spreadsheetId == "sheet-id"
            assert range == "Despesas!A:E"
            return DummyGet()

    class DummySheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: DummyValues())

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.validate_expense_row_tool._get_sheets_service",
        lambda: DummySheets(),
    )
    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.validate_expense_row_tool.TelegramAdapterService",
        lambda: SimpleNamespace(resolve_spreadsheet_id=lambda telegram_user_id: "sheet-id"),
    )

    message = validate_expense_row.entrypoint(
        date="14/09/2026",
        amount=10.25,
        description="coffee",
        category="food",
        telegram_user_id=123,
    )

    assert message == "Expense row is valid."


def test_handle_recurring_forwards_recurring_range_override(monkeypatch):
    from finance_assistant.application.handlers import telegram_handlers as handlers

    captured = {}

    class DummyFinanceAgent:
        def __init__(self, instructions=None, spreadsheet_range=None):
            captured["instructions"] = instructions
            captured["spreadsheet_range"] = spreadsheet_range

        def respond(self, message):
            return "ok"

    reply_text = AsyncMock()
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=123456789),
        message=SimpleNamespace(text="/recurring", reply_text=reply_text),
    )

    monkeypatch.setattr(handlers.telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: "sheet-id")
    monkeypatch.setattr(handlers, "FinanceAgent", DummyFinanceAgent)

    asyncio.run(handlers.handle_recurring(update, None))

    assert captured["spreadsheet_range"] == handlers.RECURRING_SPREADSHEET_RANGE
    assert captured["instructions"] == handlers.build_instructions("sheet-id", handlers.RECURRING_SPREADSHEET_RANGE)


def test_handle_audio_message_transcribes_audio_then_forwards_transcript_to_finance_agent(monkeypatch):
    from finance_assistant.application.handlers import telegram_handlers as handlers

    captured = {}

    class DummySpeechToTextAgent:
        def transcribe(self, audio_bytes):
            return "gasto de mercado"

    class DummyFinanceAgent:
        def __init__(self, instructions=None, spreadsheet_range=None):
            captured["instructions"] = instructions
            captured["spreadsheet_range"] = spreadsheet_range

        def respond(self, message):
            captured["message"] = message
            return "ok"

    class DummyFile:
        def __init__(self):
            self.download_as_bytearray = AsyncMock(return_value=b"audio-bytes")

    reply_text = AsyncMock()
    context = SimpleNamespace(bot=SimpleNamespace(get_file=lambda file_id: DummyFile()))
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=123456789),
        message=SimpleNamespace(
            audio=SimpleNamespace(file_id="abc"),
            voice=None,
            reply_text=reply_text,
        ),
        effective_message=SimpleNamespace(
            audio=SimpleNamespace(file_id="abc"),
            voice=None,
            reply_text=reply_text,
        ),
    )

    monkeypatch.setattr(handlers.telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: "sheet-id")
    monkeypatch.setattr(handlers, "SpeechToTextAgent", DummySpeechToTextAgent)
    monkeypatch.setattr(handlers, "FinanceAgent", DummyFinanceAgent)
    monkeypatch.setattr(handlers, "markdown_to_telegram_html", lambda reply: reply)

    asyncio.run(handlers.handle_audio_message(update, context))

    assert captured["message"] == "gasto de mercado"
    assert captured["spreadsheet_range"] == handlers.EXPENSES_RANGE_NAME
    assert "sheet-id" in captured["instructions"]


def test_speech_to_text_agent_transcribes_supplied_audio_bytes(monkeypatch):
    import finance_assistant.infrastructure.agents.speech_to_text_agent as speech_module

    captured = {}

    class DummyAudio:
        def __init__(self, content):
            self.content = content

    class DummyGemini:
        def __init__(self, id=None, api_key=None):
            self.id = id
            self.api_key = api_key

    class DummyAgent:
        def __init__(self, model=None, markdown=False):
            self.model = model
            self.markdown = markdown

        def run(self, prompt, audio=None):
            captured["prompt"] = prompt
            captured["audio"] = audio
            return SimpleNamespace(content="transcript text")

    monkeypatch.setattr(speech_module, "Agent", DummyAgent)
    monkeypatch.setattr(speech_module, "Audio", DummyAudio)
    monkeypatch.setattr(speech_module, "Gemini", DummyGemini)

    agent = SpeechToTextAgent()
    transcript = agent.transcribe(b"voice-buffer")

    assert transcript == "transcript text"
    assert captured["prompt"].startswith("Give a transcript")
    assert isinstance(captured["audio"], list)
    assert captured["audio"][0].content == b"voice-buffer"


def test_unknown_telegram_user_gets_registration_message_and_skips_agent(monkeypatch):
    from finance_assistant.application.handlers import telegram_handlers as handlers

    class DummyFinanceAgent:
        def __init__(self, instructions=None):
            raise AssertionError("FinanceAgent should not be constructed when no spreadsheet is registered")

    reply_text = AsyncMock()
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=999999999),
        message=SimpleNamespace(text="hello", reply_text=reply_text),
    )

    monkeypatch.setattr(handlers.telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: None)
    monkeypatch.setattr(handlers, "FinanceAgent", DummyFinanceAgent)

    asyncio.run(handlers.handle_message(update, None))

    reply_text.assert_awaited_once()
    sent_message = reply_text.await_args.args[0]
    assert "administrador" in sent_message.lower()
    assert "planilha" in sent_message.lower()
    assert "cadastro" in sent_message.lower()


def test_add_expense_tool_uses_google_sheets_append_support(monkeypatch):
    captured = {}

    class DummyAppend:
        def __init__(self, payload):
            self.payload = payload

        def execute(self):
            return {"updates": {"updatedRange": "Despesas!A4"}}

    class DummyValues:
        def append(self, spreadsheetId, range, valueInputOption, insertDataOption, body):
            captured["spreadsheetId"] = spreadsheetId
            captured["range"] = range
            captured["valueInputOption"] = valueInputOption
            captured["insertDataOption"] = insertDataOption
            captured["body"] = body
            return DummyAppend(body)

    class DummySheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: DummyValues())

    monkeypatch.setattr("finance_assistant.infrastructure.agents.add_expense_tool._get_sheets_service", lambda: DummySheets())
    monkeypatch.setattr("finance_assistant.infrastructure.agents.add_expense_tool.TelegramAdapterService", lambda: SimpleNamespace(resolve_spreadsheet_id=lambda telegram_user_id: "sheet-id"))

    message = add_expense.entrypoint(
        date="2026-09-14",
        amount=10.25,
        description="coffee",
        category="food",
        telegram_user_id=123,
    )

    assert "Expense added successfully" in message
    assert captured["spreadsheetId"] == "sheet-id"
    assert captured["range"] == "Despesas!A:E"
    assert captured["valueInputOption"] == "USER_ENTERED"
    assert captured["insertDataOption"] == "INSERT_ROWS"
    assert captured["body"] == {"values": [["🤖", "2026-09-14", 10.25, "coffee", "food"]]}


def test_telegram_adapter_service_returns_spreadsheet_for_known_telegram_user():
    service = TelegramAdapterService()

    spreadsheet_id = service.resolve_spreadsheet_id(8910318803)

    assert spreadsheet_id == "19HBfcD7gLrvMQFW9RWBezGqtvNh75acAICPevBJWAkY"


def test_telegram_adapter_service_degrades_safely_for_unknown_telegram_user():
    service = TelegramAdapterService()

    spreadsheet_id = service.resolve_spreadsheet_id(999999999)

    assert spreadsheet_id is None