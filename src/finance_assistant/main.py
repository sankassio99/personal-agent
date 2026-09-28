"""Main application entrypoint."""
import logging
from datetime import time

from finance_assistant.adapters.telegram.bot import run_bot
from finance_assistant.application.services.daily_summary_job import DailySummaryJob
from finance_assistant.application.services.daily_summary_scheduler import DailySummaryScheduler
from finance_assistant.application.services.weekly_summary_job import WeeklySummaryJob
from finance_assistant.application.services.weekly_summary_scheduler import WeeklySummaryScheduler

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Main execution entrypoint."""
    scheduler = DailySummaryScheduler(time(21, 00))
    job = DailySummaryJob()
    scheduler.start(lambda: job.run_all_users())
    weekly_scheduler = WeeklySummaryScheduler()
    weekly_job = WeeklySummaryJob()
    weekly_scheduler.start(lambda: weekly_job.run_all_users())
    run_bot()

if __name__ == "__main__":
    main()
