"""Scheduler for the weekly summary job."""

from __future__ import annotations

import logging
from datetime import datetime, time
from typing import Callable

from finance_assistant.application.services.recurrence_rule import WeeklyRecurrence
from finance_assistant.application.services.recurring_job_scheduler import RecurringJobScheduler

logger = logging.getLogger(__name__)


class WeeklySummaryScheduler:
    """Run a callback on Sundays at 9:00 PM by default."""

    def __init__(self, trigger_time: time | None = None):
        self.trigger_time = trigger_time or time(21, 0)
        self._job_scheduler = RecurringJobScheduler(
            WeeklyRecurrence(weekday=6, trigger_time=self.trigger_time)
        )

    def _compute_seconds_until_next_run(self, now: datetime) -> int:
        """Return seconds until the next Sunday trigger."""
        return self._job_scheduler._compute_seconds_until_next_run(now)

    def start(self, callback: Callable[[], object]):
        """Start the weekly scheduler in a daemon thread."""
        logger.info("Weekly summary scheduler configured for Sunday at %s.", self.trigger_time.strftime("%H:%M"))
        return self._job_scheduler.start(callback)

    def schedule(self, callback: Callable[[], object]):
        """Backward-compatible helper that starts the scheduler loop."""
        return self.start(callback)
