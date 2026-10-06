"""Handle the Telegram instructions command."""

from finance_assistant.adapters.telegram.message_builders import build_instructions_message


async def handle_instructions(update, context) -> None:
    """Send the access-request instructions."""
    user = update.effective_user or update.message.from_user
    telegram_user_id = getattr(user, "id", None)
    await update.message.reply_text(build_instructions_message(telegram_user_id))
