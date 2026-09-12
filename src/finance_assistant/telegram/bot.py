"""Telegram bot runner."""

from telegram.ext import ApplicationBuilder, MessageHandler, filters

from finance_assistant.config.settings import settings
from finance_assistant.telegram.handlers import handle_message


def run_bot() -> None:
    """Start the Telegram finance assistant bot with a static reply handler."""
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured. Set it in the environment or .env file.")

    app = ApplicationBuilder().token(settings.telegram_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
