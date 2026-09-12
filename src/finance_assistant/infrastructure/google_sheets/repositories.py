"""Google Sheets repository implementation."""

class GoogleSheetsRepository:
    """Repository implementation backed by Google Sheets."""
    def __init__(self, client: GoogleSheetsClient) -> None:
        self.client = client
