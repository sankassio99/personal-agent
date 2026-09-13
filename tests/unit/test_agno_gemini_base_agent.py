import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

from finance_assistant.application.handlers.telegram_handlers import build_start_message, markdown_to_telegram_html
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
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


def test_telegram_adapter_service_returns_spreadsheet_for_known_telegram_user():
    service = TelegramAdapterService()

    spreadsheet_id = service.resolve_spreadsheet_id(8910318803)

    assert spreadsheet_id == "19HBfcD7gLrvMQFW9RWBezGqtvNh75acAICPevBJWAkY"


def test_telegram_adapter_service_degrades_safely_for_unknown_telegram_user():
    service = TelegramAdapterService()

    spreadsheet_id = service.resolve_spreadsheet_id(999999999)

    assert spreadsheet_id is None