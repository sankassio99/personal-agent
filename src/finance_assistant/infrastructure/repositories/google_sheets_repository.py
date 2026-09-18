"""Google Sheets repository for read-style finance queries."""

from __future__ import annotations

import logging
import os
from typing import Any
from google.oauth2 import service_account
from googleapiclient.discovery import build

from finance_assistant.infrastructure.agents.add_expense_tool import _get_sheets_service

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsRepository:
    """Thin repository wrapper for the Google Sheets API."""

    def __init__(self, credentials_path: str | None = None):
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    def get_sheet(self, spreadsheet_id: str | None, sheet_name: str, filter: Any | None = None) -> list[list[Any]]:
        """Return rows from a sheet, optionally filtered by a simple predicate."""
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id is required to read the Google Sheet.")

        service = self._build_service()
        range_name = f"{sheet_name}!A:Z"

        try:
            result = (
                _get_sheets_service()
                .spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to read sheet '{sheet_name}' from spreadsheet '{spreadsheet_id}'."
            ) from exc

        rows = result.get("values", [])
                
        if filter is None:
            return rows

        filtered_rows = []
        for row in rows:
            if filter(row):
                filtered_rows.append(row)
        return filtered_rows

    def _build_service(self):
        """Build Google Sheets API client using app creds or ADC."""
        if self.credentials_path:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=SCOPES,
                )
                return build("sheets", "v4", credentials=credentials)
            except Exception as exc:  # pragma: no cover - defensive fallback
                logger.warning("Falling back to ADC because service account credentials are invalid: %s", exc)

        return build("sheets", "v4")
