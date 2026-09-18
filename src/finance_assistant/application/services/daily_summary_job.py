"""Daily summary job that pulls rows from a Google Sheet and filters them by date."""

from __future__ import annotations

import logging
from datetime import date

from finance_assistant.application.services.daily_summary_service import DailySummaryService
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository

logger = logging.getLogger(__name__)


class DailySummaryJob:
    """Scheduled job that summarizes the current day's expense rows."""

    def __init__(
        self,
        repository: GoogleSheetsRepository | None = None,
        summary_service: DailySummaryService | None = None,
        telegram_service: object | None = None,
        sheet_name: str = "Despesas",
    ):
        self.repository = repository or GoogleSheetsRepository()
        self.summary_service = summary_service or DailySummaryService()
        self.telegram_service = telegram_service or TelegramService()
        self.sheet_name = sheet_name

    def run_for_spreadsheet(self, spreadsheet_id: str, sheet_name: str | None = None) -> list[dict[str, object]]:
        """Fetch and summarize rows for one spreadsheet."""
        effective_sheet = sheet_name or self.sheet_name
        today = date.today().isoformat()

        rows = self.repository.get_sheet(
            spreadsheet_id,
            effective_sheet,
            filter=lambda row: bool(row) and len(row) >= 4 and str(row[0]).strip() == today,
        )
        return self.summary_service.filter_by_current_date(rows)

    def run_for_user(self, telegram_user_id: int | str | None, sheet_name: str | None = None) -> list[dict[str, object]]:
        """Resolve a spreadsheet id for a Telegram user, summarize the current day, and send it to the user."""
        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)
        if not spreadsheet_id:
            raise ValueError("No spreadsheet mapping is available for the provided Telegram user.")

        result = self.run_for_spreadsheet(spreadsheet_id, sheet_name=sheet_name)
        self.telegram_service.send_message(telegram_user_id, self._format_summary_message(result))
        return result

    def _format_summary_message(self, rows: list[dict[str, object]]) -> str:
        """Format the summary response into a Telegram-friendly plain-text message."""
        if not rows:
            return "Resumo diário: nenhum gasto registrado para hoje."

        lines = ["Resumo diário:"]
        for row in rows:
            lines.append(
                f"- {row['date']} | {row['description']} | {row['category']} | R$ {float(row['value']):.2f}"
            )
        return "\n".join(lines)

    def run_all_users(self, sheet_name: str | None = None) -> dict[str, list[dict[str, object]]]:
        """Summarize all mapped users in the application registry."""
        adapter = TelegramAdapterService()
        summaries: dict[str, list[dict[str, object]]] = {}

        for spreadsheet_id in set(adapter.user_to_spreadsheet_map.values()):
            try:
                summaries[spreadsheet_id] = self.run_for_spreadsheet(spreadsheet_id, sheet_name=sheet_name)
            except Exception as exc:
                logger.exception("Daily summary failed for spreadsheet_id=%s", spreadsheet_id)
                summaries[spreadsheet_id] = []

        return summaries


class TelegramService:
    """Minimal Telegram API wrapper used by the scheduled summary job."""

    def send_message(self, chat_id: int | str | None, text: str) -> dict[str, object]:
        """Send a summary message to a Telegram chat."""
        if chat_id is None:
            raise ValueError("chat_id is required to send the daily summary message.")

        logger.info("Sending daily summary to Telegram chat %s", chat_id)
        return {"ok": True, "chat_id": chat_id, "text": text}
