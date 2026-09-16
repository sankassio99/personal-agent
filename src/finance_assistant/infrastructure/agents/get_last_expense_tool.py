from __future__ import annotations

import logging
from typing import Any

from agno.tools import tool

from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.add_expense_tool import (
    SHEET_NAME,
    _get_sheets_service,
)

logger = logging.getLogger(__name__)


@tool
def get_last_expense(
    spreadsheet_id: str | None = None,
    telegram_user_id: int | str | None = None,
    sheet_name: str = SHEET_NAME,
) -> str:
    """Return the last non-empty expense row from the configured worksheet."""
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
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:E",
            )
            .execute()
        )
    except Exception as exc:
        logger.exception(
            "Unable to read the last expense from Google Sheets for spreadsheet_id=%s, sheet_name=%s",
            spreadsheet_id,
            sheet_name,
        )
        raise RuntimeError(f"Unable to read the last expense from Google Sheets: {exc}") from exc

    rows = result.get("values", [])
    last_row: list[Any] | None = next((row for row in reversed(rows) if any(str(value).strip() for value in row)), None)

    if last_row is None:
        return "No expenses found."

    return "Last expense: " + " | ".join(str(value) for value in last_row)