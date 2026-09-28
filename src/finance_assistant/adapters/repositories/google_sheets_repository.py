"""Google Sheets repository for read-style finance queries."""

from __future__ import annotations

import logging
import os
from typing import Any

from finance_assistant.adapters.google_sheets_auth import build_sheets_service

logger = logging.getLogger(__name__)


class GoogleSheetsRepository:
    """Thin repository wrapper for the Google Sheets API."""

    def __init__(self, credentials_path: str | None = None):
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    def get_sheet(self, spreadsheet_id: str | None, sheet_name: str, filter: Any | None = None) -> list[list[Any]]:
        """Return rows from a sheet, optionally filtered by a simple predicate."""
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id is required to read the Google Sheet.")

        service = self._build_service()
        range_name = f"{sheet_name}!A:Z"

        try:
            result = (
                service
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

    def get_category_budget(self, spreadsheet_id: str | None, category: str) -> dict[str, Any] | None:
        """Return the budget values for one category in the client's summary sheet."""
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id is required to read the Google Sheet.")

        try:
            result = (
                self._build_service()
                .spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range="'Sumário'!B27:F42")
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to read category budgets from spreadsheet '{spreadsheet_id}'."
            ) from exc

        for row in result.get("values", []):
            if row and str(row[0]).strip() == category.strip():
                return {
                    "category": row[0],
                    "planned": row[2] if len(row) > 2 else None,
                    "actual": row[3] if len(row) > 3 else None,
                    "difference": row[4] if len(row) > 4 else None,
                }
        return None

    def _build_service(self):
        """Build Google Sheets API client using the shared service account."""
        return build_sheets_service(self.credentials_path)
