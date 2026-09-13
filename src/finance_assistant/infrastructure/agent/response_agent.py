"""Gemini-backed response adapter for message generation."""

import logging

from finance_assistant.infrastructure.agent.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class GeminiResponseAgent(BaseAgent):
    """Response adapter that builds a message-oriented agent around Gemini."""

    def __init__(self, instructions: str = "You are a helpful finance assistant.", **kwargs):
        logger.info("GeminiResponseAgent starting initialization.")
        super().__init__(**kwargs)
        self.agent = self._create_agent(instructions=instructions)
        logger.info("GeminiResponseAgent ready with configured instructions.")

    def respond(self, message: str) -> str:
        """Return the generated model response string for the given message."""
        logger.info("Starting response generation for incoming message: %s", message)
        result = self.agent.run(message)
        response_text = getattr(result, "content", str(result))
        logger.info("Response text generated: %s", response_text)
        return response_text
