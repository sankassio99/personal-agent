"""Main application entrypoint."""
import logging
from datetime import time

from finance_assistant.adapters.telegram.bot import run_bot
from finance_assistant.application.services.daily_summary_job import DailySummaryJob
from finance_assistant.application.services.daily_summary_scheduler import DailySummaryScheduler

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Main execution entrypoint."""
    scheduler = DailySummaryScheduler(time(20, 0))
    job = DailySummaryJob()
    scheduler.start(lambda: job.run_all_users)
    # job.run_for_user(8910318803, "Despesas")
    run_bot()

if __name__ == "__main__":
    main()
