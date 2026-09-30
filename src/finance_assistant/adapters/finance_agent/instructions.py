"""Build instructions for the shared finance response agent."""

from __future__ import annotations

from datetime import datetime

from finance_assistant.adapters.agents.prompts import FINANCE_ASSISTANT_PROMPT


def build_instructions(
    spreadsheet_id: str | None = None,
    spreadsheet_range: str | None = None,
    income_spreadsheet_range: str = "'Rendimentos'!B:E",
) -> str:
    """Build the agent prompt for the selected spreadsheet workflow."""
    instructions = FINANCE_ASSISTANT_PROMPT
    today = datetime.now().strftime("%d/%m/%Y")
    instructions += f" The current date is {today}."

    if spreadsheet_id:
        instructions += ". You have access to a Google Sheet with the ID: " + spreadsheet_id + "."

    if spreadsheet_range:
        instructions += " The active spreadsheet range is: " + spreadsheet_range + "."

    if spreadsheet_range == income_spreadsheet_range:
        instructions += (
            " This is the income workflow. Read and record income only in the Rendimentos tab. "
            "Use get_last_income to inspect the existing format before using add_income. "
            "If the user does not provide a category, use get_available_categories with entry_type "
            "'income' before inferring one. Use only a returned category; if none matches, ask the "
            "user for a category and do not add the income. Preserve a category explicitly provided "
            "by the user. Use DD/MM/YYYY for dates and use the current date when one is not supplied."
        )

    return instructions