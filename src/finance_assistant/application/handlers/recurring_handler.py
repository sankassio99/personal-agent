"""Handle the Telegram recurring command."""

from finance_assistant.application.handlers.finance_reply_dispatcher import _build_dispatcher

RECURRING_SPREADSHEET_RANGE = "'Recorrentes'!A1:E50"


async def handle_recurring(update, context) -> None:
    """Route the recurring command through its spreadsheet range."""
    message = update.message.text or ""
    await _build_dispatcher().dispatch(update, message, RECURRING_SPREADSHEET_RANGE)