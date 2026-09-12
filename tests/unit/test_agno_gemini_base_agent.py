import importlib

from finance_assistant.agent.base_agent import BaseAgent
from finance_assistant.agent.response_agent import GeminiResponseAgent
from finance_assistant.config import settings as settings_module
from finance_assistant.config.settings import settings


def test_google_environment_settings_are_exposed_in_settings_surface(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("GOOGLE_PROJECT_ID", "test-project-id")

    importlib.reload(settings_module)

    assert settings_module.settings.google_client_id == "test-client-id"
    assert settings_module.settings.google_client_secret == "test-client-secret"
    assert settings_module.settings.google_project_id == "test-project-id"


def test_google_sheets_repository_and_client_can_be_created_from_placeholder_contract():
    from finance_assistant.infrastructure.google_sheets.client import GoogleSheetsClient
    from finance_assistant.infrastructure.google_sheets.repositories import GoogleSheetsRepository

    client = GoogleSheetsClient(credentials_path="")
    repository = GoogleSheetsRepository(client)

    assert isinstance(client, GoogleSheetsClient)
    assert repository.client is client


def test_base_agent_selects_gemini_flash_lite_model(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key", raising=False)

    base = BaseAgent()

    assert base.model.id == "gemini-2.5-flash-lite"
    assert base.model.api_key == "test-key"


def test_gemini_response_agent_can_wrap_agent_run(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key", raising=False)

    response_agent = GeminiResponseAgent(instructions="You answer finance questions.")

    assert response_agent.agent is not None
    assert response_agent.agent.instructions == "You answer finance questions."
