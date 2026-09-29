"""Scheduled job that delivers weekly expense summaries."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from finance_assistant.application.services.daily_summary_job import TelegramService
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.application.services.weekly_summary_message_formatter import WeeklySummaryMessageFormatter
from finance_assistant.application.services.weekly_summary_service import WeeklySummaryService
from finance_assistant.infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository

logger = logging.getLogger(__name__)


class WeeklySummaryJob:
    """Fetch, aggregate, and deliver a weekly summary for each mapped user."""

    def __init__(
        self,
        repository: GoogleSheetsRepository | None = None,
        summary_service: WeeklySummaryService | None = None,
        telegram_service: object | None = None,
        message_formatter: WeeklySummaryMessageFormatter | None = None,
        sheet_name: str = "Despesas",
        reference_date: date | None = None,
    ):
        self.repository = repository or GoogleSheetsRepository()
        self.summary_service = summary_service or WeeklySummaryService()
        self.telegram_service = telegram_service or TelegramService()
        self.message_formatter = message_formatter or WeeklySummaryMessageFormatter()
        self.sheet_name = sheet_name
        self.reference_date = reference_date

    def _reference_date(self) -> date:
        return self.reference_date or date.today()

    def run_for_spreadsheet(self, spreadsheet_id: str, sheet_name: str | None = None) -> dict[str, object]:
        """Fetch and summarize the completed week for one spreadsheet."""
        rows = self.repository.get_sheet(spreadsheet_id, sheet_name or self.sheet_name)
        return self.summary_service.summarize(rows, reference_date=self._reference_date())

    def run_for_user(self, telegram_user_id: int | str | None, sheet_name: str | None = None) -> dict[str, object]:
        """Resolve a user's spreadsheet, summarize its week, and send the result."""
        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)
        if not spreadsheet_id:
            logger.warning("Weekly summary skipped because no mapping exists for user=%s.", telegram_user_id)
            raise ValueError("No spreadsheet mapping is available for the provided Telegram user.")

        result = self.run_for_spreadsheet(spreadsheet_id, sheet_name)
        self.sendMessage(telegram_user_id, result)
        return result

    def sendMessage(self, telegram_user_id: int | str | None, result: dict[str, object]) -> None:
        """Format and deliver one weekly summary."""
        message = self.message_formatter.format(result)
        logger.info("Sending weekly summary message to telegram_user_id=%s", telegram_user_id)
        self.telegram_service.send_message(telegram_user_id, message)

    def run_all_users(self, sheet_name: str | None = None) -> None:
        """Deliver a weekly summary to every mapped user without cross-user failures."""
        adapter = TelegramAdapterService()
        for user_id, spreadsheet_id in adapter.user_to_spreadsheet_map.items():
            try:
                result = self.run_for_spreadsheet(spreadsheet_id, sheet_name)
                self.sendMessage(user_id, result)
            except Exception:
                logger.exception("Weekly summary failed for telegram_user_id=%s.", user_id)
