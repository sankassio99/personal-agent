"""Handle the Telegram recurring command."""

from telegram.constants import ParseMode

from finance_assistant.adapters.finance_agent.instructions import build_instructions
from finance_assistant.adapters.telegram.message_builders import build_unregistered_user_message
from finance_assistant.adapters.telegram.message_formatter import markdown_to_telegram_html
from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.add_expense_tool import telegram_user_context
from finance_assistant.infrastructure.agents.response_agent import FinanceAgent

RECURRING_SPREADSHEET_RANGE = "'Recorrentes'!A1:E50"


async def handle_recurring(update, context) -> None:
    """Route the recurring command through its spreadsheet range."""
    message = update.message.text or ""
    user = update.effective_user or update.message.from_user
    telegram_user_id = getattr(user, "id", None)
    spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)

    if not spreadsheet_id:
        await update.message.reply_text(build_unregistered_user_message(telegram_user_id))
        return

    finance_agent = FinanceAgent(
        instructions=build_instructions(spreadsheet_id, RECURRING_SPREADSHEET_RANGE),
        spreadsheet_range=RECURRING_SPREADSHEET_RANGE,
    )
    with telegram_user_context(telegram_user_id):
        reply = finance_agent.respond(message)

    await update.message.reply_text(markdown_to_telegram_html(reply), parse_mode=ParseMode.HTML)