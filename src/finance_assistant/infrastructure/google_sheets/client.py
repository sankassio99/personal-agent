"""Google Sheets API client."""

class GoogleSheetsClient:
    """Client for connecting to Google Sheets API."""
    def __init__(self, credentials_path: str = "") -> None:
        self.credentials_path = credentials_path
