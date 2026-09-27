"""Scheduler for the daily summary job."""

from __future__ import annotations

import logging
from datetime import datetime, time

from finance_assistant.application.services.recurrence_rule import DailyRecurrence
from finance_assistant.application.services.recurring_job_scheduler import RecurringJobScheduler

logger = logging.getLogger(__name__)


class DailySummaryScheduler:
    """Small scheduler helper that runs a callback every day at a configured trigger time (default 8:00 PM)."""

    def __init__(self, trigger_time: time | None = None):
        self.trigger_time = trigger_time or time(20, 0)
        self._job_scheduler = RecurringJobScheduler(DailyRecurrence(self.trigger_time))

    def _compute_seconds_until_next_run(self, now: datetime) -> int:
        """Return the number of seconds until the next configured trigger time."""
        return self._job_scheduler._compute_seconds_until_next_run(now)

    def start(self, callback):
        """Start the scheduler in a daemon thread so it runs in the background."""
        logger.info("Daily summary scheduler configured for %s", self.trigger_time.strftime("%H:%M"))
        return self._job_scheduler.start(callback)

    def schedule(self, callback):
        """Backward-compatible helper that starts the scheduler loop."""
        return self.start(callback)

