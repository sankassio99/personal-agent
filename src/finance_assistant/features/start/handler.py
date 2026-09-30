"""Handle the Telegram start command."""

from finance_assistant.adapters.telegram.message_builders import build_start_message


async def handle_start(update, context) -> None:
    """Send onboarding guidance for the current Telegram user."""
    user = update.effective_user or update.message.from_user
    telegram_user_id = getattr(user, "id", None)
    await update.message.reply_text(build_start_message(telegram_user_id))