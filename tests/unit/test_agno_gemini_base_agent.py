import importlib

from finance_assistant.application.handlers.telegram_handlers import markdown_to_telegram_html
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