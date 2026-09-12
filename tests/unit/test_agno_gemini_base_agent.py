from finance_assistant.agent.base_agent import BaseAgent
from finance_assistant.agent.response_agent import GeminiResponseAgent
from finance_assistant.config.settings import settings


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
