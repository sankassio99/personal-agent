"""Speech-to-text adapter using the repository’s Agno/Gemini configuration pattern."""

import logging
import os
from google.genai import types
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
        self.prompt = prompt or (
            "Give a transcript of this audio message as plain text only. "
            "Remove filler words and speaker labels if they are not needed."
        )
        
        self.model_id = model_id or getattr(settings, "gemini_model_id", "gemini-2.5-flash-lite")
        self.api_key = api_key or getattr(settings, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        
        self.model = Gemini(
                    id=self.model_id, 
                    api_key=self.api_key,
                    model_type="output_model"
                )
        
        self.agent = Agent(model=self.model)

    def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe a Telegram audio byte payload and normalize the result into a transcript string."""
        if not audio_bytes:
            logger.warning("Speech-to-text transcription requested with empty audio bytes.")
            return ""

        result = self.agent.run(self.prompt, audio=[Audio(content=audio_bytes)])
        
        content = getattr(result, "content", str(result))
        
        logger.info("___________________________________________________________")
        logger.info("Speech-to-text agent produced content: %s", content)
        logger.info("___________________________________________________________")
            
        return content
