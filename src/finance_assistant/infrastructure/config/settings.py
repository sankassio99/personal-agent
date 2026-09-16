"""Settings loader using environment variables."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""

    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    google_sheets_credentials: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_project_id: str = os.getenv("GOOGLE_PROJECT_ID", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model_id: str = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash-lite")


settings = Settings()
