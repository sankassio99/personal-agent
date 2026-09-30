"""Route a Telegram command to the finance reply dispatcher."""

from finance_assistant.application.handlers.finance_reply_dispatcher import _build_dispatcher

EXPENSES_SPREADSHEET_RANGE = "'Despesas'!B1:E"


async def handle_finance_command(update, context) -> None:
    """Forward the command text using the selected spreadsheet range."""
    message = update.message.text or ""
    await _build_dispatcher().dispatch(update, message, EXPENSES_SPREADSHEET_RANGE)