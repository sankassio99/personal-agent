"""Reusable base agent abstraction for the finance assistant project."""

import logging
import os

from finance_assistant.infrastructure.config.settings import settings
from agno.tools.google.sheets import GoogleSheetsTools

from finance_assistant.infrastructure.agents.add_expense_tool import add_expense
from finance_assistant.infrastructure.agents.get_last_expense_tool import get_last_expense

logger = logging.getLogger(__name__)

try:
    from agno.agent import Agent
    from agno.models.google import Gemini
except Exception:
    class Gemini:
        """Fallback Gemini model object used when Agno is unavailable."""

        def __init__(self, id: str = "gemini-2.5-flash-lite", api_key: str = ""):
            self.id = id
            self.api_key = api_key

    class Agent:
        """Fallback Agno-like Agent object used when Agno is unavailable."""

        def __init__(self, model=None, instructions: str = "", **kwargs):
            self.model = model
            self.instructions = instructions
            self.kwargs = kwargs

        def run(self, message: str, **kwargs):
            class Response:
                def __init__(self, content: str):
                    self.content = content

            logger.info("Fallback Agent.run produced a response for message: %s", message)
            return Response(f"Fallback agent reply for: {message}")


SAMPLE_RANGE_NAME = "'Despesas'!B1:E"
SUMMARY_RANGE_NAME = "'Sumário'!B27:F42"
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class BaseAgent:
    """Base abstraction for model-backed agents in the repo.

    Inspired by the JARVIS project’s lightweight BaseAgent pattern but kept
    compatible with the current finance assistant package structure.
    """

    def __init__(self, model_id: str | None = None, api_key: str | None = None, spreadsheet_range: str | None = None):
        self.model_id = model_id or getattr(settings, "gemini_model_id", "gemini-2.5-flash-lite")
        self.api_key = api_key or getattr(settings, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        self.spreadsheet_range = spreadsheet_range or SAMPLE_RANGE_NAME
        logger.info("BaseAgent configured with model_id=%s", self.model_id)
        self.model = Gemini(id=self.model_id, api_key=self.api_key)
        logger.info("BaseAgent attached Gemini model object for response flow.")

    def _create_agent(self, instructions: str, spreadsheet_range: str | None = None, **kwargs):
        """Create an Agno-style agent from a common model configuration."""
        range_to_use = spreadsheet_range or self.spreadsheet_range or SAMPLE_RANGE_NAME
        
        google_sheets_tool = GoogleSheetsTools(
            spreadsheet_range=range_to_use,
            oauth_port=8080,
            scopes=SHEETS_SCOPES,
            update_sheet=True,
            create_sheet=True,
            read_sheet=True
        )

        logger.info("Creating Agent with instructions length=%s", len(instructions))
        return Agent(
            tools=[google_sheets_tool, get_last_expense, add_expense],
            model=self.model,
            instructions=instructions,
            **kwargs,
        )

