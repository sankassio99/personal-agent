"""Gemini-backed response adapter for message generation."""

import logging

from finance_assistant.infrastructure.agents.base_agent import BaseAgent
from finance_assistant.infrastructure.agents.prompts import FINANCE_ASSISTANT_PROMPT

logger = logging.getLogger(__name__)


class FinanceAgent(BaseAgent):
    """Response adapter that builds a message-oriented agent around Gemini."""

    def __init__(self, instructions: str = FINANCE_ASSISTANT_PROMPT, spreadsheet_range: str | None = None, **kwargs):
        super().__init__(spreadsheet_range=spreadsheet_range, **kwargs)
        logger.info("FinanceAgent starting initialization.")

        self.agent = self._create_agent(instructions=instructions, spreadsheet_range=self.spreadsheet_range)

        logger.info("FinanceAgent ready with configured instructions.")

    def respond(self, message: str) -> str:
        """Return the generated model response string for the given message."""
        logger.info("Starting response generation for incoming message: %s", message)

        result = self.agent.run(message)
        response_text = getattr(result, "content", str(result))

        logger.info("Response text generated: %s", response_text)

        return response_text
