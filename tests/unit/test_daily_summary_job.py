from datetime import date, datetime, time

from finance_assistant.application.services.daily_summary_job import DailySummaryJob
from finance_assistant.application.services.daily_summary_service import DailySummaryService
from finance_assistant.application.services.daily_summary_scheduler import DailySummaryScheduler


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
    )

    result = job.run_for_user(8910318803)

    assert result == [{"date": "2026-09-18", "value": 12.5, "description": "Lunch", "category": "Food"}]
    assert job.telegram_service.calls[0]["chat_id"] == 8910318803
    assert "Lunch" in job.telegram_service.calls[0]["text"]
