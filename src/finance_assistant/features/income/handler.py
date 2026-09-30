"""Handle the Telegram income command."""

from telegram.constants import ParseMode

from finance_assistant.adapters.finance_agent.instructions import build_instructions
from finance_assistant.adapters.telegram.message_builders import build_unregistered_user_message
from finance_assistant.adapters.telegram.message_formatter import markdown_to_telegram_html
from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
from finance_assistant.adapters.agents.add_expense_tool import telegram_user_context
from finance_assistant.adapters.agents.response_agent import FinanceAgent

INCOME_SPREADSHEET_RANGE = "'Rendimentos'!B:E"
INCOME_INSTRUCTIONS = (
    " This is the income workflow. Read and record income only in the Rendimentos tab. "
    "Use get_last_income to inspect the existing format before using add_income. "
    "If the user does not provide a category, use get_available_categories with entry_type "
    "'income' before inferring one. Use only a returned category; if none matches, ask the "
    "user for a category and do not add the income. Preserve a category explicitly provided "
    "by the user. Use DD/MM/YYYY for dates and use the current date when one is not supplied."
)


def build_income_instructions(spreadsheet_id: str) -> str:
    """Build common FinanceAgent instructions plus income workflow rules."""
    return build_instructions(spreadsheet_id, INCOME_SPREADSHEET_RANGE) + INCOME_INSTRUCTIONS


async def handle_income(update, context) -> None:
    """Route the income command through its spreadsheet range."""
    message = update.message.text or ""
    user = update.effective_user or update.message.from_user
    telegram_user_id = getattr(user, "id", None)
    spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)

    if not spreadsheet_id:
        await update.message.reply_text(build_unregistered_user_message(telegram_user_id))
        return

    finance_agent = FinanceAgent(
        instructions=build_income_instructions(spreadsheet_id),
        spreadsheet_range=INCOME_SPREADSHEET_RANGE,
    )
    with telegram_user_context(telegram_user_id):
        reply = finance_agent.respond(message)

    await update.message.reply_text(markdown_to_telegram_html(reply), parse_mode=ParseMode.HTML)