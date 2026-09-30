"""Orchestrate spreadsheet resolution, agent execution, and Telegram delivery."""

from __future__ import annotations

from telegram.constants import ParseMode

from finance_assistant.application.handlers.build_instructions import build_instructions
from finance_assistant.application.handlers.build_unregistered_user_message import build_unregistered_user_message
from finance_assistant.application.handlers.markdown_to_telegram_html import markdown_to_telegram_html
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.add_expense_tool import telegram_user_context
from finance_assistant.infrastructure.agents.response_agent import FinanceAgent


def _build_dispatcher() -> "FinanceReplyDispatcher":
    """Compose the finance reply workflow used by Telegram handlers."""
    return FinanceReplyDispatcher(
        telegram_adapter_service=TelegramAdapterService(),
        finance_agent_factory=FinanceAgent,
        instructions_builder=build_instructions,
        unregistered_message_builder=build_unregistered_user_message,
        reply_formatter=markdown_to_telegram_html,
    )


class FinanceReplyDispatcher:
    """Resolve a user, run the finance agent, and deliver the formatted reply."""

    def __init__(
        self,
        telegram_adapter_service,
        finance_agent_factory,
        instructions_builder,
        unregistered_message_builder,
        reply_formatter,
        user_context_factory=telegram_user_context,
    ):
        self.telegram_adapter_service = telegram_adapter_service
        self.finance_agent_factory = finance_agent_factory
        self.instructions_builder = instructions_builder
        self.unregistered_message_builder = unregistered_message_builder
        self.reply_formatter = reply_formatter
        self.user_context_factory = user_context_factory

    async def dispatch(
        self,
        update,
        message_text: str,
        spreadsheet_range: str,
    ) -> None:
        """Resolve the user, generate a finance response, and send formatted HTML."""
        user = update.effective_user or update.message.from_user
        telegram_user_id = getattr(user, "id", None)
        spreadsheet_id = self.telegram_adapter_service.resolve_spreadsheet_id(telegram_user_id)

        if not spreadsheet_id:
            await update.message.reply_text(self.unregistered_message_builder(telegram_user_id))
            return

        with self.user_context_factory(telegram_user_id):
            reply = self.generate_reply(message_text, spreadsheet_range, spreadsheet_id)

        await update.message.reply_text(self.reply_formatter(reply), parse_mode=ParseMode.HTML)

    def generate_reply(
        self,
        message_text: str,
        spreadsheet_range: str,
        spreadsheet_id: str,
    ) -> str:
        """Build the finance agent, execute it in the user's context, and return its reply."""
        finance_agent = self.finance_agent_factory(
            instructions=self.instructions_builder(spreadsheet_id, spreadsheet_range),
            spreadsheet_range=spreadsheet_range,
        )
        return finance_agent.respond(message_text)