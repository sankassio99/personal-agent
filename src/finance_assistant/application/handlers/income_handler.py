"""Handle the Telegram income command."""

from finance_assistant.application.handlers.finance_reply_dispatcher import _build_dispatcher

INCOME_SPREADSHEET_RANGE = "'Rendimentos'!B:E"


async def handle_income(update, context) -> None:
    """Route the income command through its spreadsheet range."""
    message = update.message.text or ""
    await _build_dispatcher().dispatch(update, message, INCOME_SPREADSHEET_RANGE)