"""Recurrence rule abstractions for computing when a recurring job should run next."""

from __future__ import annotations

import calendar
from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta


class RecurrenceRule(ABC):
    """Compute the next run time for a recurring job."""

    @abstractmethod
    def next_run(self, after: datetime) -> datetime:
        """Return the next datetime, strictly after `after`, at which this rule should trigger."""
        raise NotImplementedError


class DailyRecurrence(RecurrenceRule):
    """Trigger once every day at a fixed time."""

    def __init__(self, trigger_time: time):
        self.trigger_time = trigger_time

    def next_run(self, after: datetime) -> datetime:
        candidate = datetime.combine(after.date(), self.trigger_time)
        if candidate < after:
            candidate += timedelta(days=1)
        return candidate


class WeeklyRecurrence(RecurrenceRule):
    """Trigger once every week on a fixed weekday (0=Monday .. 6=Sunday) and time."""

    def __init__(self, weekday: int, trigger_time: time):
        if not 0 <= weekday <= 6:
            raise ValueError("weekday must be between 0 (Monday) and 6 (Sunday).")
        self.weekday = weekday
        self.trigger_time = trigger_time

    def next_run(self, after: datetime) -> datetime:
        candidate = datetime.combine(after.date(), self.trigger_time)
        days_ahead = (self.weekday - candidate.weekday()) % 7
        candidate += timedelta(days=days_ahead)
        if candidate <= after:
            candidate += timedelta(days=7)
        return candidate


class MonthlyRecurrence(RecurrenceRule):
    """Trigger once every month on a fixed day-of-month and time, skipping months that lack that day."""

    def __init__(self, day_of_month: int, trigger_time: time):
        if not 1 <= day_of_month <= 31:
            raise ValueError("day_of_month must be between 1 and 31.")
        self.day_of_month = day_of_month
        self.trigger_time = trigger_time

    def next_run(self, after: datetime) -> datetime:
        year, month = after.year, after.month
        # Bounded: the configured day exists in at least one month within any 12-month span.
        for _ in range(24):
            days_in_month = calendar.monthrange(year, month)[1]
            if self.day_of_month <= days_in_month:
                candidate = datetime.combine(datetime(year, month, self.day_of_month).date(), self.trigger_time)
                if candidate > after:
                    return candidate
            year, month = self._next_month(year, month)
        raise ValueError(f"Could not compute next run for day_of_month={self.day_of_month}.")

    @staticmethod
    def _next_month(year: int, month: int) -> tuple[int, int]:
        if month == 12:
            return year + 1, 1
        return year, month + 1
