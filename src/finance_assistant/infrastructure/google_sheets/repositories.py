"""Google Sheets repository implementation."""

from typing import Iterable, Any

from finance_assistant.infrastructure.google_sheets.client import GoogleSheetsClient


class GoogleSheetsRepository:
    """Repository implementation backed by Google Sheets.

    Keeps the repository aligned with the existing placeholder package shape
    while exposing a simple read/write surface for callbacks and tests.
    """

    def __init__(self, client: GoogleSheetsClient | None = None):
        self.client = client or GoogleSheetsClient()

    def read(self, spreadsheet_id: str | None = None, spreadsheet_range: str | None = None) -> list[list[Any]]:
        """Read rows from the configured spreadsheet."""
        return self.client.read_sheet(spreadsheet_id=spreadsheet_id, spreadsheet_range=spreadsheet_range)

    def write(self, values: Iterable[Iterable[Any]], spreadsheet_id: str | None = None,
              spreadsheet_range: str | None = None) -> bool:
        """Write rows to the configured spreadsheet."""
        return self.client.update_sheet(values, spreadsheet_id=spreadsheet_id, spreadsheet_range=spreadsheet_range)
