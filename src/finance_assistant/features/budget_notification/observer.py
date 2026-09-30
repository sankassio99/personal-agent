"""React to recorded expenses with budget notifications."""

from __future__ import annotations

import logging

from finance_assistant.adapters.services.event_bus import ExpenseRecorded
from finance_assistant.features.budget_notification.service import BudgetNotificationService

logger = logging.getLogger(__name__)


class BudgetNotificationObserver:
    """Translate an expense event into a best-effort budget notification."""

    def __init__(self, service_factory=BudgetNotificationService):
        self.service_factory = service_factory

    def handle(self, event: ExpenseRecorded) -> None:
        """Notify the budget feature after an expense has been recorded."""
        try:
            self.service_factory().notify_if_needed(event.telegram_user_id, event.category)
        except Exception:
            logger.exception(
                "Budget notification failed after expense was recorded for telegram_user_id=%s, category=%s",
                event.telegram_user_id,
                event.category,
            )