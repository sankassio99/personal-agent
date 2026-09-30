"""Handle the Telegram summary command."""

from finance_assistant.application.handlers.finance_reply_dispatcher import _build_dispatcher

SUMMARY_SPREADSHEET_RANGE = "'Sumário'!B18:H"


async def handle_summary(update, context) -> None:
    """Route the summary command through its spreadsheet range."""
    message = update.message.text or ""
    await _build_dispatcher().dispatch(update, message, SUMMARY_SPREADSHEET_RANGE)