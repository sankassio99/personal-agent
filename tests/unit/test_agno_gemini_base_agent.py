import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from finance_assistant.adapters.finance_agent.instructions import build_instructions
from finance_assistant.adapters.telegram.message_builders import (
    build_help_message,
    build_start_message,
    build_unregistered_user_message,
)
from finance_assistant.adapters.telegram.message_formatter import markdown_to_telegram_html
from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
from finance_assistant.features.audio.handler import handle_audio_message
from finance_assistant.features.income.handler import INCOME_SPREADSHEET_RANGE, handle_income
from finance_assistant.features.message.handler import EXPENSES_SPREADSHEET_RANGE, handle_message
from finance_assistant.features.recurring.handler import RECURRING_SPREADSHEET_RANGE, handle_recurring
from finance_assistant.adapters.agents.speech_to_text_agent import SpeechToTextAgent
from finance_assistant.adapters.agents.add_expense_tool import add_expense
from finance_assistant.adapters.agents.base_agent import BaseAgent
from finance_assistant.adapters.agents.response_agent import FinanceAgent
from finance_assistant import settings as settings_module
from finance_assistant.settings import settings


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
    prompt = build_instructions("sheet-id", "'Recorrentes'!A1:E50")

    assert "sheet-id" in prompt
    assert "'Recorrentes'!A1:E50" in prompt


def test_base_agent_create_agent_accepts_spreadsheet_range_override(monkeypatch):
    import finance_assistant.adapters.agents.base_agent as base_agent_module

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
    assert agent.tools[4].name == "get_last_income"
    assert agent.tools[5].name == "add_income"
    assert agent.tools[6].name == "get_available_categories"


def test_get_last_expense_reads_the_last_non_empty_sheet_row(monkeypatch):
    from finance_assistant.adapters.agents.get_last_expense_tool import get_last_expense

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
    from finance_assistant.adapters.agents.validate_expense_row_tool import validate_expense_row

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

    telegram_adapter_service = TelegramAdapterService()
    monkeypatch.setattr(telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: "sheet-id")
    monkeypatch.setattr(
        "finance_assistant.features.recurring.handler.TelegramAdapterService",
        lambda: telegram_adapter_service,
    )
    monkeypatch.setattr(
        "finance_assistant.features.recurring.handler.FinanceAgent",
        DummyFinanceAgent,
    )

    asyncio.run(handle_recurring(update, None))

    assert captured["spreadsheet_range"] == RECURRING_SPREADSHEET_RANGE
    assert captured["instructions"] == build_instructions("sheet-id", RECURRING_SPREADSHEET_RANGE)


def test_handle_income_forwards_income_range_override(monkeypatch):
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
        message=SimpleNamespace(text="/rendimentos", reply_text=reply_text),
    )

    telegram_adapter_service = TelegramAdapterService()
    monkeypatch.setattr(telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: "sheet-id")
    monkeypatch.setattr(
        "finance_assistant.features.income.handler.TelegramAdapterService",
        lambda: telegram_adapter_service,
    )
    monkeypatch.setattr(
        "finance_assistant.features.income.handler.FinanceAgent",
        DummyFinanceAgent,
    )

    asyncio.run(handle_income(update, None))

    assert captured["spreadsheet_range"] == INCOME_SPREADSHEET_RANGE
    assert "get_last_income" in captured["instructions"]
    assert "get_available_categories" in captured["instructions"]


def test_help_message_includes_rendimentos_command():
    assert "/rendimentos" in build_help_message()
    assert "registra rendimentos" in build_help_message()


def test_handle_audio_message_transcribes_audio_then_forwards_transcript_to_finance_agent(monkeypatch):
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
            self.download_to_memory = AsyncMock(side_effect=lambda buffer: buffer.write(b"audio-bytes"))

    reply_text = AsyncMock()
    context = SimpleNamespace(bot=SimpleNamespace(get_file=AsyncMock(return_value=DummyFile())))
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

    telegram_adapter_service = TelegramAdapterService()
    monkeypatch.setattr(telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: "sheet-id")
    monkeypatch.setattr(
        "finance_assistant.features.audio.handler.TelegramAdapterService",
        lambda: telegram_adapter_service,
    )
    monkeypatch.setattr(
        "finance_assistant.features.audio.handler.FinanceAgent",
        DummyFinanceAgent,
    )
    monkeypatch.setattr(
        "finance_assistant.features.audio.handler.SpeechToTextAgent",
        DummySpeechToTextAgent,
    )

    asyncio.run(handle_audio_message(update, context))

    assert captured["message"] == "gasto de mercado"
    assert captured["spreadsheet_range"] == EXPENSES_SPREADSHEET_RANGE
    assert "sheet-id" in captured["instructions"]


def test_speech_to_text_agent_transcribes_supplied_audio_bytes(monkeypatch):
    import finance_assistant.adapters.agents.speech_to_text_agent as speech_module

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
    class DummyFinanceAgent:
        def __init__(self, instructions=None):
            raise AssertionError("FinanceAgent should not be constructed when no spreadsheet is registered")

    reply_text = AsyncMock()
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=999999999),
        message=SimpleNamespace(text="hello", reply_text=reply_text),
    )

    telegram_adapter_service = TelegramAdapterService()
    monkeypatch.setattr(telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: None)
    monkeypatch.setattr(
        "finance_assistant.features.message.handler.TelegramAdapterService",
        lambda: telegram_adapter_service,
    )
    monkeypatch.setattr(
        "finance_assistant.features.message.handler.FinanceAgent",
        DummyFinanceAgent,
    )

    asyncio.run(handle_message(update, None))

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


def test_get_last_income_reads_rendimentos_columns_for_mapped_user(monkeypatch):
    from finance_assistant.adapters.agents.get_last_income_tool import get_last_income

    captured = {}

    class Request:
        def execute(self):
            return {"values": [["14/09/2026", "100.00", "Salary", "Work"]]}

    class Values:
        def get(self, spreadsheetId, range):
            captured["spreadsheetId"] = spreadsheetId
            captured["range"] = range
            return Request()

    class Sheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: Values())

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_last_income_tool._get_sheets_service",
        lambda: Sheets(),
    )
    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_last_income_tool.TelegramAdapterService",
        lambda: SimpleNamespace(resolve_spreadsheet_id=lambda telegram_user_id: "sheet-id"),
    )

    assert get_last_income.entrypoint(telegram_user_id=123) == "Last income: 14/09/2026 | 100.00 | Salary | Work"
    assert captured == {"spreadsheetId": "sheet-id", "range": "Rendimentos!B:E"}


def test_get_last_income_rejects_unmapped_user():
    from finance_assistant.adapters.agents.get_last_income_tool import get_last_income

    with pytest.raises(ValueError, match="No Google spreadsheet id"):
        get_last_income.entrypoint(telegram_user_id=999999999)


def test_add_income_appends_to_rendimentos_columns(monkeypatch):
    from finance_assistant.adapters.agents.add_income_tool import add_income

    captured = {}

    class Request:
        def execute(self):
            return {"updates": {"updatedRange": "Rendimentos!B4:E4"}}

    class Values:
        def append(self, **kwargs):
            captured.update(kwargs)
            return Request()

    class Sheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: Values())

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.add_income_tool._get_sheets_service",
        lambda: Sheets(),
    )
    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.add_income_tool.TelegramAdapterService",
        lambda: SimpleNamespace(resolve_spreadsheet_id=lambda telegram_user_id: "sheet-id"),
    )

    assert "Income added successfully" in add_income.entrypoint(
        date="14/09/2026",
        amount=100.0,
        description="Salary",
        category="Work",
        telegram_user_id=123,
    )
    assert captured == {
        "spreadsheetId": "sheet-id",
        "range": "Rendimentos!B:E",
        "valueInputOption": "USER_ENTERED",
        "insertDataOption": "INSERT_ROWS",
        "body": {"values": [["14/09/2026", 100.0, "Salary", "Work"]]},
    }


def test_add_income_propagates_google_sheets_failure(monkeypatch):
    from finance_assistant.adapters.agents.add_income_tool import add_income

    class Values:
        def append(self, **kwargs):
            raise RuntimeError("write failed")

    class Sheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: Values())

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.add_income_tool._get_sheets_service",
        lambda: Sheets(),
    )

    with pytest.raises(RuntimeError, match="Unable to append the income record"):
        add_income.entrypoint(
            date="14/09/2026",
            amount=100.0,
            description="Salary",
            category="Work",
            spreadsheet_id="sheet-id",
        )


@pytest.mark.parametrize(
    ("entry_type", "expected_range", "values", "expected_message"),
    [
        (
            "expense",
            "Sumário!B30:B42",
            [["Supermercado"], [], [" Transporte "]],
            "Available expense categories: Supermercado, Transporte",
        ),
        (
            "income",
            "Sumário!B49:B53",
            [["Salário"], [""], ["Freelance"]],
            "Available income categories: Salário, Freelance",
        ),
    ],
)
def test_get_available_categories_reads_the_configured_summary_range(
    monkeypatch,
    entry_type,
    expected_range,
    values,
    expected_message,
):
    from finance_assistant.adapters.agents.get_available_categories_tool import get_available_categories

    captured = {}

    class Request:
        def execute(self):
            return {"values": values}

    class SheetsValues:
        def get(self, spreadsheetId, range):
            captured["spreadsheetId"] = spreadsheetId
            captured["range"] = range
            return Request()

    class Sheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: SheetsValues())

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_available_categories_tool._get_sheets_service",
        lambda: Sheets(),
    )
    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_available_categories_tool.TelegramAdapterService",
        lambda: SimpleNamespace(resolve_spreadsheet_id=lambda telegram_user_id: "sheet-id"),
    )

    assert get_available_categories.entrypoint(entry_type, telegram_user_id=123) == expected_message
    assert captured == {"spreadsheetId": "sheet-id", "range": expected_range}


def test_get_available_categories_rejects_unmapped_user_without_sheets_request(monkeypatch):
    from finance_assistant.adapters.agents.get_available_categories_tool import get_available_categories

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_available_categories_tool.TelegramAdapterService",
        lambda: SimpleNamespace(resolve_spreadsheet_id=lambda telegram_user_id: None),
    )
    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_available_categories_tool._get_sheets_service",
        lambda: pytest.fail("Google Sheets must not be accessed for an unmapped user."),
    )

    with pytest.raises(ValueError, match="No Google spreadsheet id"):
        get_available_categories.entrypoint("expense", telegram_user_id=999999999)


def test_get_available_categories_propagates_google_sheets_failures(monkeypatch):
    from finance_assistant.adapters.agents.get_available_categories_tool import get_available_categories

    class SheetsValues:
        def get(self, **kwargs):
            raise RuntimeError("read failed")

    class Sheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: SheetsValues())

    monkeypatch.setattr(
        "finance_assistant.infrastructure.agents.get_available_categories_tool._get_sheets_service",
        lambda: Sheets(),
    )

    with pytest.raises(RuntimeError, match="Unable to read expense categories"):
        get_available_categories.entrypoint("expense", spreadsheet_id="sheet-id")


def test_expense_prompt_requires_category_retrieval_only_when_omitted():
    from finance_assistant.adapters.agents.prompts import FINANCE_ASSISTANT_PROMPT

    assert 'get_available_categories with entry_type "expense"' in FINANCE_ASSISTANT_PROMPT
    assert "Preserve a category explicitly provided by the user." in FINANCE_ASSISTANT_PROMPT
    assert "if none matches, ask the user for a category and do not add the expense" in FINANCE_ASSISTANT_PROMPT


def test_income_tools_reuse_the_expense_google_sheets_service_builder():
    from finance_assistant.adapters.agents.add_expense_tool import _get_sheets_service as expense_service
    from finance_assistant.adapters.agents.add_income_tool import _get_sheets_service as income_append_service
    from finance_assistant.adapters.agents.get_last_income_tool import _get_sheets_service as income_read_service

    assert income_append_service is expense_service
    assert income_read_service is expense_service


def test_telegram_adapter_service_returns_spreadsheet_for_known_telegram_user():
    service = TelegramAdapterService()

    spreadsheet_id = service.resolve_spreadsheet_id(8910318803)

    assert spreadsheet_id == "19HBfcD7gLrvMQFW9RWBezGqtvNh75acAICPevBJWAkY"


def test_telegram_adapter_service_returns_spreadsheet_for_newly_registered_telegram_user():
    service = TelegramAdapterService()

    spreadsheet_id = service.resolve_spreadsheet_id(6853832500)

    assert spreadsheet_id == "1zTmoe-_-QDn9f64C7lxLNEzjvrlN_173cqJ52WHm7Cg"


def test_telegram_adapter_service_degrades_safely_for_unknown_telegram_user():
    service = TelegramAdapterService()

    spreadsheet_id = service.resolve_spreadsheet_id(999999999)

    assert spreadsheet_id is None