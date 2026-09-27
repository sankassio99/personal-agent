## Why

The finance assistant already sends a daily expense summary at a fixed time each day, but users have no way to see how their spending trends across a full week without manually reviewing each day's message. A weekly summary grouped by category gives users a higher-level view of where their money went, complementing the daily summary without replacing it.

## What Changes

- Add a scheduled weekly job that triggers once a week (Sunday at 21:00 local time) using the existing generic recurrence/scheduler infrastructure (`WeeklyRecurrence` + `RecurringJobScheduler`).
- Add a weekly summary service that reads a user's spreadsheet rows through the existing `GoogleSheetsRepository.get_sheet(...)` contract, filters rows to the trailing 7-day window (the prior Sunday through Saturday), and aggregates the total value per category.
- Add a weekly summary message formatter that renders a Telegram message grouping totals by category (with an emoji per category and a sensible default for unmapped categories), showing the week's date range and a grand total.
- Reuse the existing Telegram delivery path (`TelegramAdapterService` + `TelegramService`) to send the formatted weekly summary to every mapped user, following the same per-user iteration and error-isolation pattern as the daily summary job.
- Wire the weekly scheduler and job into the application entrypoint alongside the existing daily summary scheduler.

## Capabilities

### New Capabilities
- `weekly-summary-job`: Add a scheduled weekly summary capability that reads a user's sheet data, aggregates it by category over the trailing 7-day window, and delivers a category-grouped Telegram message with a weekly total.

## Impact

- Affects the finance assistant's background scheduling layer (`main.py` entrypoint) by registering an additional recurring job alongside the daily summary job.
- Adds new application-layer services (weekly summary service, weekly summary message formatter, weekly summary job) modeled after the existing daily summary services, with no changes to the `GoogleSheetsRepository` or `RecurringJobScheduler` contracts.
- No changes to existing daily summary behavior; the weekly job runs independently and on its own schedule.
