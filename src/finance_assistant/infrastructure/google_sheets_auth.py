"""Shared Google Sheets service-account authentication helpers."""

from __future__ import annotations

import os
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheets_credentials(credentials_path: str | None = None) -> service_account.Credentials:
    """Load the configured service-account credentials for Google Sheets."""
    path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not path:
        raise RuntimeError(
            "GOOGLE_APPLICATION_CREDENTIALS must point to a Google service-account credentials file."
        )

    try:
        return service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    except Exception as exc:
        raise RuntimeError(f"Unable to load Google Sheets service-account credentials: {exc}") from exc


def build_sheets_service(credentials_path: str | None = None) -> Any:
    """Build a Google Sheets API service using the shared service account."""
    return build("sheets", "v4", credentials=get_sheets_credentials(credentials_path))
