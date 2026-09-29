from __future__ import annotations

import logging
import os
from typing import Any

from agno.tools import tool

from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.google_sheets_auth import build_sheets_service

logger = logging.getLogger(__name__)

SHEET_NAME = os.getenv("EXPENSE_SHEET_NAME", "Despesas")


def _get_sheets_service() -> Any:
    """Return a Google Sheets service using the shared service account."""
    return build_sheets_service()


@tool
def add_expense(
    date: str,
    amount: float,
    description: str,
    category: str,
    spreadsheet_id: str | None = None,
    telegram_user_id: int | str | None = None,
    sheet_name: str = SHEET_NAME,
) -> str:
    """
    Add a new expense to the configured Google Sheets worksheet.

    The tool automatically appends the expense to the next available row.
    Never specify a row number to this helper.
    """
    logger.info(
        "Starting add_expense tool for telegram_user_id=%s, sheet_name=%s, date=%s, amount=%s, description=%s, category=%s",
        telegram_user_id,
        sheet_name,
        date,
        amount,
        description,
        category,
    )

    if spreadsheet_id is None:
        logger.info("Resolving spreadsheet_id for telegram_user_id=%s", telegram_user_id)
        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)
        logger.info("Resolved spreadsheet_id=%s for telegram_user_id=%s", spreadsheet_id, telegram_user_id)

    if not spreadsheet_id:
        logger.error(
            "No Google spreadsheet id could be resolved for telegram_user_id=%s. "
            "The add_expense tool requires spreadsheet_id explicitly or a Telegram user mapping.",
            telegram_user_id,
        )
        raise ValueError(
            "No Google spreadsheet id could be resolved for the active user. "
            "Provide spreadsheet_id explicitly or route through TelegramAdapterService."
        )

    values = [["🤖", date, amount, description, category]]

    try:
        sheets = _get_sheets_service()
        logger.info("Google Sheets service built successfully for spreadsheet_id=%s", spreadsheet_id)
    except Exception as exc:
        logger.exception("Unable to build Google Sheets service for spreadsheet_id=%s", spreadsheet_id)
        raise RuntimeError(f"Unable to build Google Sheets service: {exc}") from exc

    try:
        logger.info("Appending expense row to Google Sheets")
        result = (
            sheets.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:E",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": values},
            )
            .execute()
        )
    except Exception as exc:
        logger.exception(
            "Unable to append expense row to Google Sheets for spreadsheet_id=%s, sheet_name=%s, telegram_user_id=%s",
            spreadsheet_id,
            sheet_name,
            telegram_user_id,
        )
        raise RuntimeError(f"Unable to append the expense row to Google Sheets: {exc}") from exc

    updated_range = result.get("updates", {}).get("updatedRange", "unknown")
    logger.info("Expense append finished successfully. spreadsheet_id=%s, updatedRange=%s", spreadsheet_id, updated_range)
    return f"Expense added successfully. Range: {updated_range}"