"""Daily summary job that pulls rows from a Google Sheet and filters them by date."""

from __future__ import annotations

import asyncio
import inspect
import logging
from datetime import date

from finance_assistant.application.services.daily_summary_service import DailySummaryService
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.config.settings import settings
from finance_assistant.infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository
from telegram import Bot

logger = logging.getLogger(__name__)

class DailySummaryJob:
    """Scheduled job that summarizes the current day's expense rows."""

    def __init__(
        self,
        repository: GoogleSheetsRepository | None = None,
        summary_service: DailySummaryService | None = None,
        telegram_service: object | None = None,
        sheet_name: str = "Despesas",
        today: date | None = None,
    ):
        self.repository = repository or GoogleSheetsRepository()
        self.summary_service = summary_service or DailySummaryService()
        self.telegram_service = telegram_service or TelegramService()
        self.sheet_name = sheet_name
        self.today = today or date.today()

    def run_for_spreadsheet(self, spreadsheet_id: str, sheet_name: str | None = None) -> list[dict[str, object]]:
        """Fetch and summarize rows for one spreadsheet."""
        effective_sheet = sheet_name or self.sheet_name
        rows = self.repository.get_sheet(
            spreadsheet_id,
            effective_sheet
        )

        return self.summary_service.filter_by_current_date(rows, today=self.today)

    def run_for_user(self, telegram_user_id: int | str | None, sheet_name: str | None = None) -> list[dict[str, object]]:
        """Resolve a spreadsheet id for a Telegram user, summarize the current day, and send it to the user."""
        logger.info("Starting daily summary for telegram_user_id=%s", telegram_user_id)

        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)
        if not spreadsheet_id:
            logger.warning("Daily summary skipped for telegram_user_id=%s because no spreadsheet mapping exists.", telegram_user_id)
            raise ValueError("No spreadsheet mapping is available for the provided Telegram user.")

        logger.info(
            "Resolved telegram_user_id=%s to spreadsheet_id=%s for daily summary.",
            telegram_user_id,
            spreadsheet_id,
        )

        result = self.run_for_spreadsheet(spreadsheet_id, sheet_name=sheet_name)
        
        logger.info(
            "Daily summary for telegram_user_id=%s produced %s record(s).",
            telegram_user_id,
            len(result),
        )

        self.sendMessage(telegram_user_id, result)
        
        return result

    def sendMessage(self, telegram_user_id, result):
        message = self._format_summary_daily_message(result)
        logger.info("Sending daily summary message to telegram_user_id=%s", telegram_user_id)
        
        logger.info("___________________________________________________________")
        logger.info("message: %s", message)
        logger.info("___________________________________________________________")
        
        self.telegram_service.send_message(telegram_user_id, message)

    def _format_summary_daily_message(self, rows: list[dict[str, object]]) -> str:
        """Format the summary response into a Telegram-friendly plain-text message."""
        if not rows:
            return "📋 <b>Resumo de Gastos de Hoje</b>:\n\nNenhum gasto registrado para hoje."

        total = sum(float(row["value"]) for row in rows)
        today = self.today.strftime("%d/%m/%Y")

        lines = [
            f"📋 <b>Resumo de Gastos de Hoje ({today})</b>:",
            ""
        ]

        for row in rows:
            lines.append(
                f"•  {row['description']}: €{float(row['value']):.2f} ({row['category']})"
            )

        lines.extend([
            "",
            f"💰 <b>Total gasto hoje</b>: €{total:.2f}",
        ])
        return "\n".join(lines)

    def run_all_users(self, sheet_name: str | None = None):
        """Summarize all mapped users in the application registry."""
        adapter = TelegramAdapterService()
        logger.info("___________________________________________________________")
        logger.info("run_all_users")
        logger.info("___________________________________________________________")

        for user_id in set(adapter.user_to_spreadsheet_map.keys()):
            spreadsheet_id = adapter.user_to_spreadsheet_map[user_id]
            
            try:
                logger.info("___________________________________________________________")
                logger.info("run_for_spreadsheet for user: %s", user_id)
                logger.info("___________________________________________________________")
                
                result = self.run_for_spreadsheet(spreadsheet_id, sheet_name=sheet_name)
                
                self.sendMessage(user_id, result)
                
            except Exception as exc:
                logger.exception("Daily summary failed for spreadsheet_id=%s", spreadsheet_id)


class TelegramService:
    """Telegram API wrapper used by the scheduled summary job."""

    def __init__(self, token: str | None = None):
        self.token = token or settings.telegram_token

    def send_message(self, chat_id: int | str | None, text: str) -> dict[str, object]:
        """Send a summary message to a Telegram chat."""
        if chat_id is None:
            raise ValueError("chat_id is required to send the daily summary message.")
        if not self.token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured. Set it in the environment or .env file.")

        bot = Bot(token=self.token)
        logger.info("Sending daily summary to Telegram chat %s", chat_id)
        response = bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

        if inspect.isawaitable(response):
            response = asyncio.run(response)

        if isinstance(response, dict):
            message_id = response.get("message_id")
        else:
            message_id = getattr(response, "message_id", None)

        return {"ok": True, "chat_id": chat_id, "text": text, "message_id": message_id}
