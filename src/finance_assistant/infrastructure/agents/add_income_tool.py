"""Google Sheets tool for recording income entries."""

from __future__ import annotations

import logging

from agno.tools import tool

from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.add_expense_tool import _get_sheets_service
from finance_assistant.infrastructure.agents.get_last_income_tool import INCOME_RANGE

logger = logging.getLogger(__name__)


@tool
def add_income(
    date: str,
    amount: float,
    description: str,
    category: str,
    spreadsheet_id: str | None = None,
    telegram_user_id: int | str | None = None,
) -> str:
    """Append one income record to columns B through E of Rendimentos."""
    if spreadsheet_id is None:
        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)

    if not spreadsheet_id:
        raise ValueError(
            "No Google spreadsheet id could be resolved for the active user. "
            "Provide spreadsheet_id explicitly or route through TelegramAdapterService."
        )

    values = [[date, amount, description, category]]
    try:
        result = (
            _get_sheets_service()
            .spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=INCOME_RANGE,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": values},
            )
            .execute()
        )
    except Exception as exc:
        logger.exception(
            "Unable to append income for spreadsheet_id=%s.",
            spreadsheet_id,
        )
        raise RuntimeError("Unable to append the income record to Google Sheets.") from exc

    updated_range = result.get("updates", {}).get("updatedRange", "unknown")
    return f"Income added successfully. Range: {updated_range}"
