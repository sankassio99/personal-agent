"""Google Sheets tool for reading the latest income entry."""

from __future__ import annotations

import logging
from typing import Any

from agno.tools import tool

from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.add_expense_tool import _get_sheets_service

logger = logging.getLogger(__name__)

INCOME_SHEET_NAME = "Rendimentos"
INCOME_RANGE = f"{INCOME_SHEET_NAME}!B:E"


@tool
def get_last_income(
    spreadsheet_id: str | None = None,
    telegram_user_id: int | str | None = None,
) -> str:
    """Return the latest non-empty income record from the Rendimentos tab."""
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
            .get(spreadsheetId=spreadsheet_id, range=INCOME_RANGE)
            .execute()
        )
    except Exception as exc:
        logger.exception(
            "Unable to read income records for spreadsheet_id=%s.",
            spreadsheet_id,
        )
        raise RuntimeError("Unable to read income records from Google Sheets.") from exc

    rows = result.get("values", [])
    last_row: list[Any] | None = next(
        (row for row in reversed(rows) if any(str(value).strip() for value in row)),
        None,
    )
    if last_row is None:
        return "No income records found."

    return "Last income: " + " | ".join(str(value) for value in last_row)
