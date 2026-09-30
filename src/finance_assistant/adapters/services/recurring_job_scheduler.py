"""Generic scheduler loop that runs a callback according to a RecurrenceRule."""

from __future__ import annotations

import logging
import threading
import time as time_module
from datetime import datetime
from typing import Callable

from finance_assistant.adapters.services.recurrence_rule import RecurrenceRule

logger = logging.getLogger(__name__)


class RecurringJobScheduler:
    """Run a callback repeatedly according to a recurrence rule, in a background daemon thread."""

    def __init__(self, recurrence: RecurrenceRule, callback: Callable[[], object] | None = None):
        self.recurrence = recurrence
        self.callback = callback

    def _compute_seconds_until_next_run(self, now: datetime) -> int:
        """Return the number of seconds until the recurrence rule's next run."""
        next_run = self.recurrence.next_run(now)
        return int((next_run - now).total_seconds())

    def _run_loop(self, callback: Callable[[], object] | None):
        """Block until the next trigger and then execute the callback, repeating indefinitely."""
        while True:
            seconds_until_run = self._compute_seconds_until_next_run(datetime.now())

            time_module.sleep(seconds_until_run)

            try:
                if callback is not None:
                    callback()
            except Exception:
                logger.exception("Recurring job execution failed for the scheduled run.")

    def start(self, callback: Callable[[], object] | None = None) -> threading.Thread:
        """Start the scheduler in a daemon thread so it runs in the background."""
        effective_callback = callback or self.callback
        logger.info("Recurring job scheduler started for rule=%s", type(self.recurrence).__name__)
        thread = threading.Thread(target=self._run_loop, args=(effective_callback,), daemon=True)
        thread.start()
        return thread

    def schedule(self, callback: Callable[[], object] | None = None) -> threading.Thread:
        """Backward-compatible helper that starts the scheduler loop."""
        return self.start(callback)
