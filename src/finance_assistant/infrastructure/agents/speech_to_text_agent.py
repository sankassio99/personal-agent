"""Speech-to-text adapter using the repository’s Agno/Gemini configuration pattern."""

import logging
import os
from types import SimpleNamespace

from finance_assistant.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

try:
    from agno.agent import Agent
    from agno.media import Audio
    from agno.models.google import Gemini
except Exception:
    Agent = None
    Audio = None
    Gemini = None


class SpeechToTextAgent:
    """Return a plain-text transcript for Telegram audio bytes using an Agno Gemini model when available."""

    def __init__(self, model_id: str | None = None, api_key: str | None = None, prompt: str | None = None):
        self.model_id = model_id or getattr(settings, "gemini_model_id", "gemini-2.0-flash-exp")
        self.api_key = api_key or getattr(settings, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        self.prompt = prompt or (
            "Give a transcript of this audio message as plain text only. "
            "Remove filler words and speaker labels if they are not needed."
        )

        self.agent = None
        if Agent is not None and Gemini is not None and Audio is not None:
            try:
                self.agent = Agent(model=Gemini(id=self.model_id, api_key=self.api_key), markdown=True)
            except Exception as exc:
                logger.warning("Unable to construct Agno/Gemini speech-to-text agent: %s", exc)

    def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe a Telegram audio byte payload and normalize the result into a transcript string."""
        if not audio_bytes:
            return ""

        if self.agent is None:
            logger.warning("SpeechToTextAgent fallback engaged; returning the raw audio byte placeholder transcript.")
            return "Audio message received but no speech-to-text model is configured."

        try:
            result = self.agent.run(self.prompt, audio=[Audio(content=audio_bytes)])
            content = getattr(result, "content", str(result))
            if not isinstance(content, str):
                content = str(content)
            return content.strip()
        except TypeError:
            try:
                result = self.agent.run(self.prompt, audio=Audio(content=audio_bytes))
                content = getattr(result, "content", str(result))
                return str(content).strip()
            except Exception as exc:
                logger.warning("Speech-to-text agent fallback to typed transcript failed: %s", exc)
                return ""
        except Exception as exc:
            logger.warning("Speech-to-text transcription failed: %s", exc)
            return ""
