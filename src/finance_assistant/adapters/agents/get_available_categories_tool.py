"""Google Sheets tool for retrieving user-configured entry categories."""

from __future__ import annotations

import logging

from agno.tools import tool

from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
from finance_assistant.adapters.agents.add_expense_tool import _get_sheets_service

logger = logging.getLogger(__name__)

CATEGORY_RANGES = {
    "expense": "Sumário!B30:B42",
    "income": "Sumário!B49:B53",
}


@tool
def get_available_categories(
    entry_type: str,
    spreadsheet_id: str | None = None,
    telegram_user_id: int | str | None = None,
) -> str:
    """Return non-empty categories configured for an expense or income entry."""
    if entry_type not in CATEGORY_RANGES:
        raise ValueError("entry_type must be either 'expense' or 'income'.")

    if spreadsheet_id is None:
        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)

    if not spreadsheet_id:
        raise ValueError(
            "No Google spreadsheet id could be resolved for the active user. "
            "Provide spreadsheet_id explicitly or route through TelegramAdapterService."
        )

    try:
        result = (
            _get_sheets_service()
            .spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=CATEGORY_RANGES[entry_type])
            .execute()
        )
    except Exception as exc:
        logger.exception(
            "Unable to read %s categories for spreadsheet_id=%s.",
            entry_type,
            spreadsheet_id,
        )
        raise RuntimeError(f"Unable to read {entry_type} categories from Google Sheets.") from exc

    categories = [
        str(row[0]).strip()
        for row in result.get("values", [])
        if row and str(row[0]).strip()
    ]
    return f"Available {entry_type} categories: " + ", ".join(categories)
