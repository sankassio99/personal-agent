"""Telegram bot runner."""

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from finance_assistant.features.audio.handler import handle_audio_message
from finance_assistant.features.help.handler import handle_help
from finance_assistant.features.income.handler import handle_income
from finance_assistant.features.message.handler import handle_message
from finance_assistant.features.recurring.handler import handle_recurring
from finance_assistant.features.start.handler import handle_start
from finance_assistant.features.summary.handler import handle_summary
from finance_assistant.settings import settings

def run_bot() -> None:
    """Start the Telegram finance assistant bot with command and message handlers."""
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured. Set it in the environment or .env file.")

    app = ApplicationBuilder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("sumario", handle_summary))
    app.add_handler(CommandHandler("recorrente", handle_recurring))
    app.add_handler(CommandHandler("rendimentos", handle_income))
    app.add_handler(CommandHandler("ajuda", handle_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio_message))
    app.run_polling()
