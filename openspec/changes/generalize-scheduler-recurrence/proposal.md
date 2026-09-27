## Why

`DailySummaryScheduler` only knows how to compute "seconds until the next 8/9 PM" and runs a single hardcoded callback once a day. There is no reusable notion of a recurrence rule, so adding a weekly or monthly summary (or any other periodic job) today means copy-pasting the scheduler class and reimplementing the "compute next run" math for each new cadence. We need an architecture that lets the application register any number of recurring jobs (daily, weekly, monthly, or custom), each with its own trigger and callback, without duplicating the scheduling loop.

## What Changes

- Introduce a `RecurrenceRule` abstraction (e.g. `DailyRecurrence`, `WeeklyRecurrence`, `MonthlyRecurrence`) that only knows how to compute the next run `datetime` given a reference time. Custom cadences can be added by implementing the same interface.
- Generalize the scheduling loop into a `RecurringJobScheduler` (or similar) that accepts a `RecurrenceRule` plus a callback and owns the sleep/execute/reschedule loop, replacing the daily-only logic currently duplicated in `DailySummaryScheduler`.
- Refactor `DailySummaryScheduler` to become a thin daily-recurrence configuration (or be replaced outright by `RecurringJobScheduler(DailyRecurrence(...), callback)`), preserving its current public behavior (`start`, `schedule`) so `main.py` keeps working.
- Allow the application entrypoint (`main.py`) to register multiple jobs with different recurrence rules (e.g. daily summary at 21:00, a future weekly/monthly summary) side by side.
- **BREAKING**: `DailySummaryScheduler`'s internal `_compute_seconds_until_next_run` becomes a delegated call into a `DailyRecurrence` rule; any test or caller relying on that private method directly must update to the new rule-based API.

## Capabilities

### New Capabilities
- `recurring-job-scheduling`: Add a general-purpose recurrence architecture (recurrence rules + a job scheduler loop) that supports daily, weekly, monthly, and custom cadences for background jobs.

### Modified Capabilities
<!-- None: the daily summary job's observable schedule (daily, configurable trigger time) is unchanged; only its internal implementation now delegates to the shared recurrence architecture. -->

## Impact

- Affects `src/finance_assistant/application/services/daily_summary_scheduler.py` and its unit tests.
- Affects `src/finance_assistant/main.py`, where jobs are registered against the scheduler.
- Adds new modules for recurrence rules and the generic recurring job scheduler under `src/finance_assistant/application/services/`.
- No changes to the Google Sheets repository, summary service, message formatter, or Telegram delivery paths.
