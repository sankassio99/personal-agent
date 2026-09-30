import asyncio
from datetime import date, datetime, time
from types import SimpleNamespace

import pytest

from finance_assistant.application.services.daily_summary_job import DailySummaryJob
from finance_assistant.application.services.daily_summary_message_formatter import DailySummaryMessageFormatter
from finance_assistant.application.services.daily_summary_service import DailySummaryService
from finance_assistant.application.services.daily_summary_scheduler import DailySummaryScheduler
from finance_assistant.adapters.telegram.telegram_service import TelegramService
from finance_assistant.infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository


def test_daily_summary_service_filters_current_day_and_shapes_payload():
    service = DailySummaryService()

    rows = [
        ["2026-09-18", "12.50", "Lunch", "Food"],
        ["2026-09-17", "30.00", "Groceries", "House"],
        ["2026-09-18", "7.40", "Taxi", "Transport"],
    ]

    result = service.filter_by_current_date(rows, today=date(2026, 9, 18))

    assert result == [
        {"date": "2026-09-18", "value": 12.5, "description": "Lunch", "category": "Food"},
        {"date": "2026-09-18", "value": 7.4, "description": "Taxi", "category": "Transport"},
    ]


def test_daily_summary_scheduler_uses_8pm_target_time():
    scheduler = DailySummaryScheduler(trigger_time=time(20, 0))

    delay = scheduler._compute_seconds_until_next_run(datetime(2026, 9, 18, 19, 30))

    assert delay == 1800


def test_daily_summary_message_formatter_formats_summary_message_with_total():
    formatter = DailySummaryMessageFormatter()
    rows = [
        {"date": "2026-09-18", "value": 10.0, "description": "Remédio Bupropiona", "category": "Saúde"},
        {"date": "2026-09-18", "value": 9.98, "description": "Remédio Bupropiona", "category": "Extras"},
    ]

    today_date = date.today()
    today = today_date.strftime("%d/%m/%Y")
    message = formatter.format(rows, today_date)

    assert message == (
        f"📋 <b>Resumo de Gastos de Hoje ({today})</b>:\n\n"
        "•  Remédio Bupropiona: €10.00 (Saúde)\n"
        "•  Remédio Bupropiona: €9.98 (Extras)\n\n"
        "💰 <b>Total gasto hoje</b>: €19.98"
    )


def test_daily_summary_service_handles_brazilian_dates_and_currency_values():
    service = DailySummaryService()

    rows = [
        ["Bot", "Data", "Valor", "Descrição", "Categoria"],
        ["", "01/04/2026", "€233.63", "Continente", "Supermercado"],
        ["", "30/03/2026", "€20.00", "Taxi", "Transporte"],
        ["", "02/04/2026", "€15.50", "Mercado", "Supermercado"],
    ]

    result = service.filter_by_current_date(rows, today=date(2026, 4, 1))

    assert result == [
        {"date": "2026-04-01", "value": 233.63, "description": "Continente", "category": "Supermercado"}
    ]


def test_daily_summary_job_sends_summary_to_telegram_user():
    class DummyTelegramService:
        def __init__(self):
            self.calls = []

        def send_message(self, chat_id, text):
            self.calls.append({"chat_id": chat_id, "text": text})
            return {"ok": True}

    class DummyRepository:
        def get_sheet(self, spreadsheet_id, sheet_name, filter=None):
            return [
                ["2026-09-18", "12.50", "Lunch", "Food"],
                ["2026-09-17", "4.00", "Old", "Food"],
            ]

    job = DailySummaryJob(
        repository=DummyRepository(),
        telegram_service=DummyTelegramService(),
        today=date(2026, 9, 18),
    )

    result = job.run_for_user(8910318803)

    assert result == [{"date": "2026-09-18", "value": 12.5, "description": "Lunch", "category": "Food"}]
    assert job.telegram_service.calls[0]["chat_id"] == 8910318803
    assert "Lunch" in job.telegram_service.calls[0]["text"]


def test_telegram_service_sends_message_when_called_inside_running_event_loop(monkeypatch):
    outer_loop = None
    request_loop = None

    class AsyncBot:
        def __init__(self, token):
            assert token == "test-token"

        async def send_message(self, chat_id, text, parse_mode):
            nonlocal request_loop
            request_loop = asyncio.get_running_loop()
            assert chat_id == 123
            assert text == "Budget alert"
            assert parse_mode == "HTML"
            return SimpleNamespace(message_id=456)

    monkeypatch.setattr("finance_assistant.adapters.telegram.telegram_service.Bot", AsyncBot)
    service = TelegramService(token="test-token")

    async def send_from_running_loop():
        nonlocal outer_loop
        outer_loop = asyncio.get_running_loop()
        return service.send_message(123, "Budget alert")

    result = asyncio.run(send_from_running_loop())

    assert result == {
        "ok": True,
        "chat_id": 123,
        "text": "Budget alert",
        "message_id": 456,
    }
    assert request_loop is not outer_loop


def test_daily_summary_job_uses_current_date_for_each_execution(monkeypatch):
    class FakeDate:
        current_dates = iter([date(2026, 9, 18), date(2026, 9, 19)])

        @classmethod
        def today(cls):
            return next(cls.current_dates)

    class DummyRepository:
        def get_sheet(self, spreadsheet_id, sheet_name):
            return [
                ["2026-09-18", "12.50", "First day", "Food"],
                ["2026-09-19", "7.40", "Second day", "Transport"],
            ]

    monkeypatch.setattr("finance_assistant.application.services.daily_summary_job.date", FakeDate)
    job = DailySummaryJob(repository=DummyRepository())

    first_result = job.run_for_spreadsheet("spreadsheet-123")
    second_result = job.run_for_spreadsheet("spreadsheet-123")

    assert first_result[0]["description"] == "First day"
    assert second_result[0]["description"] == "Second day"


def test_google_sheets_repository_raises_error_on_api_failure(monkeypatch):
    class BrokenGoogleSheetsService:
        def spreadsheets(self):
            class Values:
                def get(self, **kwargs):
                    class Request:
                        def execute(self):
                            raise RuntimeError("sheet read failed")

                    return Request()

            return type("Sheets", (), {"values": lambda self: Values()})()

    repo = GoogleSheetsRepository()
    monkeypatch.setattr(repo, "_build_service", lambda: BrokenGoogleSheetsService())

    with pytest.raises(RuntimeError, match="Failed to read sheet 'Despesas' from spreadsheet"):
        repo.get_sheet("spreadsheet-123", "Despesas")
