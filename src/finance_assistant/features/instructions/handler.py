"""Handle the Telegram instructions command."""

from finance_assistant.adapters.telegram.message_builders import build_instructions_message


async def handle_instructions(update, context) -> None:
    """Send the access-request instructions."""
    await update.message.reply_text(build_instructions_message())
