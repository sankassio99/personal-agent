## 1. Weekly summary service

- [x] 1.1 Add `WeeklySummaryService` that computes the trailing 7-day window (previous Sunday through Saturday, inclusive) from a reference date, reusing `DailySummaryService`'s row parsing/date normalization/money parsing (extract shared helpers if needed to avoid duplication).
- [x] 1.2 Implement category aggregation that sums monetary values per category for rows inside the window and returns a structured payload (e.g. list of `{category, total}` plus a `grand_total`).
- [x] 1.3 Handle rows with unparseable dates/values by skipping them (mirroring `DailySummaryService`'s existing skip/logging behavior).

## 2. Weekly summary message formatter

- [x] 2.1 Add a fixed category → emoji mapping constant (Supermercado, Commuting/Transporte, Compras diversas, Extras, etc.) with a default fallback emoji for unmapped categories, using case-insensitive/trimmed lookup.
- [x] 2.2 Add `WeeklySummaryMessageFormatter.format(...)` that renders the date range header, one line per category (emoji + category + formatted `€` value), and a final grand total line matching the requested message shape.
- [x] 2.3 Add an empty-state message for weeks with no recorded expenses.

## 3. Weekly summary job and scheduler

- [x] 3.1 Add `WeeklySummaryJob` mirroring `DailySummaryJob`'s structure: `run_for_spreadsheet`, `run_for_user`, `run_all_users` (per-user error isolation + logging), and `sendMessage`, reusing `GoogleSheetsRepository`, `TelegramAdapterService`, and the existing `TelegramService` wrapper.
- [x] 3.2 Add `WeeklySummaryScheduler` wrapping `RecurringJobScheduler(WeeklyRecurrence(weekday=6, trigger_time=time(21, 0)))` (Sunday 21:00 default), following `DailySummaryScheduler`'s pattern.
- [x] 3.3 Register the weekly scheduler and job in `main.py` alongside the existing daily summary scheduler.

## 4. Verification

- [x] 4.1 Add unit tests for the trailing 7-day window filter, including boundary dates (window start/end) and both ISO and Brazilian date formats.
- [x] 4.2 Add unit tests for category aggregation (multiple rows per category summed correctly, grand total correctness).
- [x] 4.3 Add unit tests for the message formatter, covering a multi-category message matching the requested format, the unmapped-category fallback emoji, and the empty-state message.
- [x] 4.4 Add a unit test for `WeeklySummaryScheduler`'s trigger-time computation (analogous to the existing daily scheduler test).
- [x] 4.5 Run the focused test suite to verify the weekly summary flow and scheduler wiring.
