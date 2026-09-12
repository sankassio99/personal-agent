"""Google Sheets API client.

The integration is deliberately lightweight and guarded: if the Google API
client modules are unavailable, the project still imports cleanly.
"""

import os
from typing import Any, Iterable

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except Exception:
    service_account = None
    build = None


class GoogleSheetsClient:
    """Client for connecting to Google Sheets API.

    Accepts a credentials-path or an injected optional auth object. The class
    degrades safely when Google dependencies are not installed.
    """

    def __init__(self, credentials_path: str = "", service_account_path: str | None = None,
                 spreadsheet_id: str | None = None, spreadsheet_range: str | None = None,
                 auth: Any | None = None) -> None:
        self.credentials_path = credentials_path or service_account_path or os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
        self.spreadsheet_range = spreadsheet_range or os.getenv("GOOGLE_SHEETS_SPREADSHEET_RANGE", "")
        self.auth = auth
        self.service = None

    def build_service(self):
        """Create a Google Sheets service only when the dependency surface exists."""
        if build is None or service_account is None:
            return None

        if self.auth is not None:
            return build("sheets", "v4", credentials=self.auth)

        creds_path = self.credentials_path
        if not creds_path:
            return None

        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        self.service = build("sheets", "v4", credentials=creds)
        return self.service

    def read_sheet(self, spreadsheet_id: str | None = None, spreadsheet_range: str | None = None) -> list[list[Any]]:
        """Return a lightweight placeholder list-of-rows read interface."""
        service = self.build_service()
        if service is None:
            return []

        request = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id or self.spreadsheet_id,
            range=spreadsheet_range or self.spreadsheet_range,
        )
        response = request.execute()
        values = response.get("values", [])
        return values

    def update_sheet(self, values: Iterable[Iterable[Any]], spreadsheet_id: str | None = None,
                     spreadsheet_range: str | None = None) -> bool:
        """Persist a rows payload if the optional Google API client is present."""
        service = self.build_service()
        if service is None:
            return False

        body = {"values": [list(row) for row in values]}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id or self.spreadsheet_id,
            range=spreadsheet_range or self.spreadsheet_range,
            valueInputOption="RAW",
            body=body,
        ).execute()
        return True
