"""Reusable base agent abstraction for the finance assistant project."""

import logging
import os

from finance_assistant.config.settings import settings

logger = logging.getLogger(__name__)

try:
    from agno.agent import Agent
    from agno.models.google import Gemini
except Exception:
    class Gemini:
        """Fallback Gemini model object used when Agno is unavailable."""

        def __init__(self, id: str = "gemini-3.8-flash", api_key: str = ""):
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


try:
    from finance_assistant.infrastructure.google_sheets.client import GoogleSheetsClient
    from finance_assistant.infrastructure.google_sheets.repositories import GoogleSheetsRepository
except Exception:
    GoogleSheetsClient = None
    GoogleSheetsRepository = None


class BaseAgent:
    """Base abstraction for model-backed agents in the repo.

    Inspired by the JARVIS project’s lightweight BaseAgent pattern but kept
    compatible with the current finance assistant package structure.
    """

    def __init__(self, model_id: str | None = None, api_key: str | None = None):
        self.model_id = model_id or getattr(settings, "gemini_model_id", "gemini-3.8-flash")
        self.api_key = api_key or getattr(settings, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        logger.info("BaseAgent configured with model_id=%s", self.model_id)
        self.model = Gemini(id=self.model_id, api_key=self.api_key)
        logger.info("BaseAgent attached Gemini model object for response flow.")

    def _create_agent(self, instructions: str, **kwargs):
        """Create an Agno-style agent from a common model configuration."""
        logger.info("Creating Agent with instructions length=%s", len(instructions))
        return Agent(model=self.model, instructions=instructions, **kwargs)

    def google_sheets_tool(self, spreadsheet_id: str | None = None,
                            spreadsheet_range: str | None = None,
                            credentials_path: str | None = None):
        """Return an optional Google Sheets repository object behind a config guard.

        The method is intentionally import-safe: if the optional library stack
        is unavailable, it returns None rather than raising.
        """
        if GoogleSheetsRepository is None or GoogleSheetsClient is None:
            logger.info("Google Sheets tool unavailable because the optional dependency stack is missing.")
            return None

        client = GoogleSheetsClient(
            credentials_path=credentials_path or settings.google_sheets_credentials,
            spreadsheet_id=spreadsheet_id,
            spreadsheet_range=spreadsheet_range,
        )
        return GoogleSheetsRepository(client)
