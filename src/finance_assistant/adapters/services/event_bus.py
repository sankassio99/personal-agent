"""Small synchronous event bus for cross-feature notifications."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExpenseRecorded:
    """Event emitted after an expense has been persisted successfully."""

    telegram_user_id: int | str | None
    category: str


class ExpenseRecordedObserver(Protocol):
    """Handle an expense-recorded event."""

    def handle(self, event: ExpenseRecorded) -> None: ...


class EventBus:
    """Notify registered observers without coupling the publisher to features."""

    def __init__(self):
        self._observers: list[ExpenseRecordedObserver] = []

    def subscribe(self, observer: ExpenseRecordedObserver) -> None:
        """Register an observer for future expense events."""
        self._observers.append(observer)

    def clear(self) -> None:
        """Remove all observers, primarily for isolated tests."""
        self._observers.clear()

    def publish(self, event: ExpenseRecorded) -> None:
        """Notify every observer while isolating observer failures."""
        for observer in tuple(self._observers):
            try:
                observer.handle(event)
            except Exception:
                logger.exception("Expense-recorded observer failed.")


expense_recorded_event_bus = EventBus()