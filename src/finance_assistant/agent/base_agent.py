"""Reusable base agent abstraction for the finance assistant project."""

import logging
import os
from finance_assistant.infrastructure.google_sheets.client import GoogleSheetsClient
from finance_assistant.infrastructure.google_sheets.repositories import GoogleSheetsRepository
from finance_assistant.config.settings import settings
from agno.tools.google.sheets import GoogleSheetsTools

logger = logging.getLogger(__name__)

try:
    from agno.agent import Agent
    from agno.models.google import Gemini
except Exception:
    class Gemini:
        """Fallback Gemini model object used when Agno is unavailable."""

        def __init__(self, id: str = "gemini-2.5-flash", api_key: str = ""):
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


SAMPLE_SPREADSHEET_ID = "1jmkOtmjPNscHO91fQz4JC1XiSpn7reR8CzS34YUcPKM"
SAMPLE_RANGE_NAME = "B2:E17"
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class BaseAgent:
    """Base abstraction for model-backed agents in the repo.

    Inspired by the JARVIS project’s lightweight BaseAgent pattern but kept
    compatible with the current finance assistant package structure.
    """

    def __init__(self, model_id: str | None = None, api_key: str | None = None):
        self.model_id = model_id or getattr(settings, "gemini_model_id", "gemini-2.5-flash")
        self.api_key = api_key or getattr(settings, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        logger.info("BaseAgent configured with model_id=%s", self.model_id)
        self.model = Gemini(id=self.model_id, api_key=self.api_key)
        logger.info("BaseAgent attached Gemini model object for response flow.")

    def _create_agent(self, instructions: str, **kwargs):
        """Create an Agno-style agent from a common model configuration."""
        google_sheets_tool = GoogleSheetsTools(
            spreadsheet_id=SAMPLE_SPREADSHEET_ID,
            spreadsheet_range=SAMPLE_RANGE_NAME,
            oauth_port=8080  # Porta usada para abrir o navegador e fazer a autenticação OAuth inicial
        )

        logger.info("Creating Agent with instructions length=%s", len(instructions))
        return Agent(tools=[google_sheets_tool], 
        model=self.model, instructions=instructions, **kwargs)

