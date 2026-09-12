"""Settings loader using environment variables."""
import os

class Settings:
    """Application settings."""
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    google_sheets_credentials: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")

settings = Settings()
