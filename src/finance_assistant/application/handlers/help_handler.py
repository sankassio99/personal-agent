"""Handle the Telegram help command."""

from finance_assistant.application.handlers.build_help_message import build_help_message

async def handle_help(update, context) -> None:
    """Send the available Telegram commands."""
    await update.message.reply_text(build_help_message())