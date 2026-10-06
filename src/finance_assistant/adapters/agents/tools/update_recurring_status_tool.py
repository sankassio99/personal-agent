"""Google Sheets tool for updating recurring payment statuses."""

from __future__ import annotations

import logging

from agno.tools import tool

from finance_assistant.adapters.agents.tools.add_expense_tool import (
    _active_telegram_user_id,
    _get_sheets_service,
)
from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService

logger = logging.getLogger(__name__)

RECURRING_SHEET_NAME = "Recorrentes"
RECURRING_READ_RANGE = f"{RECURRING_SHEET_NAME}!A:E"
_STATUS_VALUES = {
    "pago": "Pago",
    "paga": "Pago",
    "pendente": "Pendente",
}


def _normalize_text(value: str) -> str:
    """Normalize text used for user-input and worksheet comparisons."""
    return " ".join(value.split()).casefold()


def _normalize_status(status: str) -> str:
    """Return the canonical supported payment status."""
    normalized_status = _STATUS_VALUES.get(_normalize_text(status))
    if normalized_status is None:
        raise ValueError("Unsupported status. Use Pago or Pendente.")
    return normalized_status


@tool
def update_recurring_status(
    recurring_name: str,
    status: str,
    spreadsheet_id: str | None = None,
    telegram_user_id: int | str | None = None,
) -> str:
    """Update one uniquely matched recurring payment's status in column E."""
    normalized_status = _normalize_status(status)
    normalized_name = _normalize_text(recurring_name)
    if not normalized_name:
        raise ValueError("Recurring name must not be empty.")

    if telegram_user_id is None:
        telegram_user_id = _active_telegram_user_id.get()

    if spreadsheet_id is None:
        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)

    if not spreadsheet_id:
        raise ValueError(
            "No Google spreadsheet id could be resolved for the active user. "
            "Provide spreadsheet_id explicitly or route through TelegramAdapterService."
        )

    try:
        rows = (
            _get_sheets_service()
            .spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=RECURRING_READ_RANGE)
            .execute()
            .get("values", [])
        )
    except Exception as exc:
        logger.exception(
            "Unable to read recurring payments for spreadsheet_id=%s.",
            spreadsheet_id,
        )
        raise RuntimeError("Unable to read recurring payments from Google Sheets.") from exc

    recurring_rows = list(enumerate(rows[1:], start=2))
    matching_rows = [
        row_number
        for row_number, row in recurring_rows
        if row and _normalize_text(str(row[0])) == normalized_name
    ]
    if not matching_rows:
        available_names = [
            str(row[0]).strip()
            for _, row in recurring_rows
            if row and str(row[0]).strip()
        ]
        available_options = ", ".join(available_names) if available_names else "none"
        return (
            f'Recurring payment "{recurring_name}" was not found. '
            f"Available recurring payments: {available_options}."
        )
    if len(matching_rows) > 1:
        return (
            f'More than one recurring payment matches "{recurring_name}". '
            "Provide a more specific name."
        )

    row_number = matching_rows[0]
    try:
        result = (
            _get_sheets_service()
            .spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=f"{RECURRING_SHEET_NAME}!E{row_number}",
                valueInputOption="USER_ENTERED",
                body={"values": [[normalized_status]]},
            )
            .execute()
        )
    except Exception as exc:
        logger.exception(
            "Unable to update recurring payment status for spreadsheet_id=%s, row=%s.",
            spreadsheet_id,
            row_number,
        )
        raise RuntimeError("Unable to update recurring payment status in Google Sheets.") from exc

    updated_range = result.get("updatedRange", f"{RECURRING_SHEET_NAME}!E{row_number}")
    return f'Recurring payment "{recurring_name}" updated to {normalized_status}. Range: {updated_range}'
