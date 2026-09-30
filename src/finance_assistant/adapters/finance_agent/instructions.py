"""Build instructions for the shared finance response agent."""

from __future__ import annotations

from datetime import datetime

from finance_assistant.adapters.agents.prompts import FINANCE_ASSISTANT_PROMPT


def build_instructions(
    spreadsheet_id: str | None = None,
    spreadsheet_range: str | None = None,
) -> str:
    """Build the agent prompt for the selected spreadsheet workflow."""
    instructions = FINANCE_ASSISTANT_PROMPT
    today = datetime.now().strftime("%d/%m/%Y")
    instructions += f" The current date is {today}."

    if spreadsheet_id:
        instructions += ". You have access to a Google Sheet with the ID: " + spreadsheet_id + "."

    if spreadsheet_range:
        instructions += " The active spreadsheet range is: " + spreadsheet_range + "."

    return instructions