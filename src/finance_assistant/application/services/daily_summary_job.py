"""Daily summary job that pulls rows from a Google Sheet and filters them by date."""

from __future__ import annotations

import logging
from datetime import date

from finance_assistant.application.services.daily_summary_message_formatter import DailySummaryMessageFormatter
from finance_assistant.application.services.daily_summary_service import DailySummaryService
from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
from finance_assistant.adapters.telegram.telegram_service import TelegramService
from finance_assistant.infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository

logger = logging.getLogger(__name__)

class DailySummaryJob:
    """Scheduled job that summarizes the current day's expense rows."""

    def __init__(
        self,
        repository: GoogleSheetsRepository | None = None,
        summary_service: DailySummaryService | None = None,
        telegram_service: object | None = None,
        message_formatter: DailySummaryMessageFormatter | None = None,
        sheet_name: str = "Despesas",
        today: date | None = None,
    ):
        self.repository = repository or GoogleSheetsRepository()
        self.summary_service = summary_service or DailySummaryService()
        self.telegram_service = telegram_service or TelegramService()
        self.message_formatter = message_formatter or DailySummaryMessageFormatter()
        self.sheet_name = sheet_name
        self.today = today

    def _current_date(self) -> date:
        """Return the injected date or the date for the current execution."""
        return self.today or date.today()

    def run_for_spreadsheet(self, spreadsheet_id: str, sheet_name: str | None = None) -> list[dict[str, object]]:
        """Fetch and summarize rows for one spreadsheet."""
        effective_sheet = sheet_name or self.sheet_name
        rows = self.repository.get_sheet(
            spreadsheet_id,
            effective_sheet
        )

        return self.summary_service.filter_by_current_date(rows, today=self._current_date())

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
        message = self.message_formatter.format(result, self._current_date())
        logger.info("Sending daily summary message to telegram_user_id=%s", telegram_user_id)
        
        logger.info("___________________________________________________________")
        logger.info("message: %s", message)
        logger.info("___________________________________________________________")
        
        self.telegram_service.send_message(telegram_user_id, message)

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

