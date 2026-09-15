"""Telegram bot runner."""

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from finance_assistant.application.handlers.telegram_handlers import (
    handle_audio_message,
    handle_help,
    handle_message,
    handle_recurring,
    handle_start,
    handle_summary,
)
from finance_assistant.infrastructure.config.settings import settings


def run_bot() -> None:
    """Start the Telegram finance assistant bot with command and message handlers."""
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured. Set it in the environment or .env file.")

    app = ApplicationBuilder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("sumario", handle_summary))
    app.add_handler(CommandHandler("recorrente", handle_recurring))
    app.add_handler(CommandHandler("ajuda", handle_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio_message))
    app.run_polling()
