"""Handle ordinary Telegram text messages."""

from finance_assistant.application.handlers.finance_reply_dispatcher import _build_dispatcher

EXPENSES_SPREADSHEET_RANGE = "'Despesas'!B1:E"


async def handle_message(update, context) -> None:
    """Forward an ordinary text message using the expense spreadsheet range."""
    message = update.message.text or ""
    await _build_dispatcher().dispatch(update, message, EXPENSES_SPREADSHEET_RANGE)