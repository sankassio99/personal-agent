"""Handle the Telegram help command."""

from finance_assistant.adapters.telegram.message_builders import build_help_message


async def handle_help(update, context) -> None:
    """Send the available Telegram commands."""
    await update.message.reply_text(build_help_message())