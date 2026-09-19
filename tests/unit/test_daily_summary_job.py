from datetime import date, datetime, time

import pytest

from finance_assistant.application.services.daily_summary_job import DailySummaryJob, TelegramService
from finance_assistant.application.services.daily_summary_service import DailySummaryService
from finance_assistant.application.services.daily_summary_scheduler import DailySummaryScheduler
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


def test_daily_summary_job_formats_summary_message_with_total():
    job = DailySummaryJob()
    rows = [
        {"date": "2026-09-18", "value": 10.0, "description": "Remédio Bupropiona", "category": "Saúde"},
        {"date": "2026-09-18", "value": 9.98, "description": "Remédio Bupropiona", "category": "Extras"},
    ]

    today = date.today().strftime("%d/%m/%Y")
    message = job._format_summary_message(rows)

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


def test_telegram_service_uses_real_bot_client(monkeypatch):
    sent = {}

    class FakeBot:
        def __init__(self, token):
            self.token = token

        def send_message(self, chat_id, text):
            sent["chat_id"] = chat_id
            sent["text"] = text
            return {"ok": True, "chat_id": chat_id, "text": text}

    monkeypatch.setattr("finance_assistant.application.services.daily_summary_job.Bot", FakeBot)
    monkeypatch.setattr("finance_assistant.application.services.daily_summary_job.settings.telegram_token", "fake-token")

    service = TelegramService()
    response = service.send_message(123456789, "hello")

    assert response["ok"] is True
    assert sent == {"chat_id": 123456789, "text": "hello"}


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
