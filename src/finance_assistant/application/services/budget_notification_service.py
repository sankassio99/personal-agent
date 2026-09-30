"""Notify a client when a category approaches or exceeds its budget."""

from __future__ import annotations

import logging

from finance_assistant.application.services.daily_summary_service import DailySummaryService
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository

logger = logging.getLogger(__name__)


class BudgetNotificationService:
    """Look up category budget usage and send a qualifying Telegram alert."""

    def __init__(
        self,
        repository: GoogleSheetsRepository | None = None,
        telegram_service: object | None = None,
        telegram_adapter: TelegramAdapterService | None = None,
    ):
        self.repository = repository or GoogleSheetsRepository()
        self.telegram_adapter = telegram_adapter or TelegramAdapterService()
        if telegram_service is None:
            from finance_assistant.application.services.telegram_service import TelegramService

            telegram_service = TelegramService()
        self.telegram_service = telegram_service

    def notify_if_needed(self, telegram_user_id: int | str | None, category: str) -> bool:
        """Send a separate alert when valid category usage is above 70 percent."""
        logger.info("Budget notification processing started.")
        spreadsheet_id = self.telegram_adapter.resolve_spreadsheet_id(telegram_user_id)
        if not spreadsheet_id:
            logger.warning("Budget notification skipped: no spreadsheet mapping was found.")
            return False

        logger.debug("Spreadsheet resolved; looking up category budget data.")
        budget = self.repository.get_category_budget(spreadsheet_id, category)
        if budget is None:
            logger.info("Budget notification skipped: no matching category budget was found.")
            return False

        logger.debug("Category budget data retrieved; validating planned and actual values.")
        try:
            planned = DailySummaryService._parse_money(budget["planned"])
            actual = DailySummaryService._parse_money(budget["actual"])
        except (KeyError, TypeError, ValueError):
            logger.warning("Budget notification skipped: budget values were missing or invalid.")
            return False

        if planned <= 0 or actual < 0:
            logger.warning("Budget notification skipped: budget values were non-positive or invalid.")
            return False

        usage_percentage = actual / planned * 100
        if actual > planned:
            alert_level = "over_budget"
            message = (
                f"🚨 <b>Orçamento ultrapassado: {category}</b>\n"
                f"Gasto: €{actual:.2f} de €{planned:.2f} ({usage_percentage:.1f}%)."
            )
        elif usage_percentage > 70:
            alert_level = "near_limit"
            message = (
                f"⚠️ <b>Orçamento quase atingido: {category}</b>\n"
                f"Gasto: €{actual:.2f} de €{planned:.2f} ({usage_percentage:.1f}%)."
            )
        else:
            logger.info("Budget notification skipped: usage is at or below the alert threshold.")
            return False

        logger.info("Budget alert selected: %s.", alert_level)
        logger.debug("Sending budget notification through Telegram.")
        self.telegram_service.send_message(telegram_user_id, message)
        logger.info("Budget notification sent successfully.")
        return True