"""Main application entrypoint."""
import logging
from datetime import time

from finance_assistant.adapters.services.event_bus import expense_recorded_event_bus
from finance_assistant.adapters.telegram.bot import run_bot
from finance_assistant.features.budget_notification.observer import BudgetNotificationObserver
from finance_assistant.features.daily_summary.job import DailySummaryJob
from finance_assistant.features.daily_summary.scheduler import DailySummaryScheduler

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Main execution entrypoint."""
    expense_recorded_event_bus.subscribe(BudgetNotificationObserver())
    scheduler = DailySummaryScheduler(time(21, 00))
    job = DailySummaryJob()
    scheduler.start(lambda: job.run_all_users())
    # job.run_for_user(8910318803, "Despesas")
    run_bot()

if __name__ == "__main__":
    main()
