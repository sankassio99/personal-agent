from datetime import datetime, timedelta

from finance_assistant.adapters.services.recurrence_rule import RecurrenceRule
from finance_assistant.adapters.services.recurring_job_scheduler import RecurringJobScheduler


class FixedRecurrence(RecurrenceRule):
    """Test double that always returns a fixed delay from the reference time."""

    def __init__(self, delay_seconds: int):
        self.delay_seconds = delay_seconds

    def next_run(self, after: datetime) -> datetime:
        return after + timedelta(seconds=self.delay_seconds)


def test_recurring_job_scheduler_computes_delay_from_rule():
    scheduler = RecurringJobScheduler(FixedRecurrence(delay_seconds=42))

    delay = scheduler._compute_seconds_until_next_run(datetime(2026, 9, 18, 12, 0, 0))

    assert delay == 42


def test_recurring_job_scheduler_continues_after_callback_exception(monkeypatch):
    sleep_calls = []
    call_count = {"n": 0}

    def fake_sleep(seconds):
        sleep_calls.append(seconds)
        call_count["n"] += 1
        if call_count["n"] >= 2:
            raise StopIteration  # halt the infinite loop for the test

    def failing_then_ok_callback():
        if call_count["n"] == 1:
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "finance_assistant.adapters.services.recurring_job_scheduler.time_module.sleep",
        fake_sleep,
    )

    scheduler = RecurringJobScheduler(FixedRecurrence(delay_seconds=0))

    try:
        scheduler._run_loop(failing_then_ok_callback)
    except StopIteration:
        pass

    assert len(sleep_calls) == 2
