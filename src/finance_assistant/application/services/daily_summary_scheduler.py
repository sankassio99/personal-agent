"""Scheduler for the daily summary job."""

from __future__ import annotations

import logging
import threading
import time as time_module
from datetime import datetime, time, timedelta

logger = logging.getLogger(__name__)


class DailySummaryScheduler:
    """Small scheduler helper that calculates the next run time for a daily 8:00 PM trigger."""

    def __init__(self, trigger_time: time | None = None):
        self.trigger_time = trigger_time or time(13, 39)

    def _compute_seconds_until_next_run(self, now: datetime) -> int:
        """Return the number of seconds until the next configured trigger time."""
        next_run = datetime.combine(now.date(), self.trigger_time)
        if now <= next_run:
            return int((next_run - now).total_seconds())

        next_run += timedelta(days=1)
        return int((next_run - now).total_seconds())

    def _run_loop(self, callback):
        """Block until the next trigger and then execute the callback every day."""
        while True:
            seconds_until_run = self._compute_seconds_until_next_run(datetime.now())
            logger.info(
                "Daily summary scheduler waiting %s seconds until next run at %s",
                seconds_until_run,
                self.trigger_time.strftime("%H:%M"),
            )
            time_module.sleep(seconds_until_run)

            try:
                if callback is not None:
                    callback()
            except Exception:
                logger.exception("Daily summary job execution failed for the scheduled run.")

    def start(self, callback):
        """Start the scheduler in a daemon thread so it runs in the background."""
        logger.info("Daily summary scheduler configured for %s", self.trigger_time.strftime("%H:%M"))
        thread = threading.Thread(target=self._run_loop, args=(callback,), daemon=True)
        thread.start()
        return thread

    def schedule(self, callback):
        """Backward-compatible helper that starts the scheduler loop."""
        return self.start(callback)
