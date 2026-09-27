## Context

The finance assistant already has a working daily-summary pipeline: `DailySummaryScheduler` wraps a `RecurringJobScheduler` (driven by a `RecurrenceRule`), `DailySummaryJob` resolves each Telegram user's spreadsheet id, pulls rows through `GoogleSheetsRepository.get_sheet(...)`, filters/normalizes them via `DailySummaryService`, formats an HTML message with `DailySummaryMessageFormatter`, and delivers it through a small `TelegramService` wrapper. The recurrence layer already supports `DailyRecurrence`, `WeeklyRecurrence`, and `MonthlyRecurrence`, so a weekly job only needs its own service/formatter/job classes plus a scheduler instance configured with `WeeklyRecurrence`.

This change adds an equivalent weekly pipeline that aggregates a user's spending by category over the trailing 7-day window and sends a single grouped-by-category message, instead of listing every transaction.

## Goals / Non-Goals

**Goals:**
- Reuse the existing `WeeklyRecurrence` + `RecurringJobScheduler` building blocks; add no new scheduling primitives.
- Reuse `GoogleSheetsRepository.get_sheet(...)` and `TelegramAdapterService`/`TelegramService` exactly as the daily job does, with no contract changes.
- Add a `WeeklySummaryService` that filters rows to the trailing 7-day window (previous Sunday 00:00 through Saturday 23:59, inclusive) and aggregates total value per category.
- Add a `WeeklySummaryMessageFormatter` that renders the category-grouped message with per-category emoji, the week's date range, and a grand total, matching the requested format:
  ```
  📊 Resumo de gastos da semana (20/09/2026 a 26/09/2026):

  • 🛒 Supermercado: €49.52
  • 🚗 Commuting: €23.85
  • 🛍️ Compras diversas: €99.27
  • ➕ Extras: €74.52

  • 💰 Total da semana: €247.16
  ```
- Add a `WeeklySummaryJob` mirroring `DailySummaryJob`'s per-user iteration, error isolation (`run_all_users` continues past a single user's failure), and logging conventions.
- Register a `WeeklySummaryScheduler` in `main.py` alongside the existing `DailySummaryScheduler`, defaulting to Sunday at 21:00.

**Non-Goals:**
- Changing the daily summary job's behavior, message format, or schedule.
- Adding a new Telegram command for on-demand weekly summaries (scheduler-triggered only, matching the daily job's current scope).
- Building a generic "summary job" abstraction that unifies daily/weekly/monthly jobs; this change follows the existing pattern of a dedicated job class per cadence, consistent with how the daily job was implemented.
- Persisting category emoji mappings in configuration; a fixed in-code mapping with a default fallback emoji is sufficient.

## Decisions

1. **Aggregate by category instead of listing rows.**
   Rationale: The requested message groups and sums by category rather than listing each transaction, unlike the daily summary. `WeeklySummaryService` will return a structured payload of `{category, total}` entries (sorted by first-seen order or descending total) plus a `grand_total`, rather than reusing `DailySummaryService`'s per-row shape.

2. **Compute the trailing week as "previous Sunday through Saturday" relative to execution date.**
   Rationale: `WeeklyRecurrence` triggers on a fixed weekday/time; running the job on Sunday at 21:00 and summarizing the just-completed Sunday-Saturday window keeps the reporting period intuitive and independent of the exact trigger weekday, mirroring the example message's inclusive 7-day range (20/09 a 26/09). The window boundaries are computed in the service from an injectable "reference date" (mirroring `DailySummaryJob`'s injectable `today`) for testability.

3. **Reuse row parsing/normalization logic from `DailySummaryService` rather than duplicating it.**
   Rationale: Both jobs read the same spreadsheet shape (5-column rows with date/value/description/category, Brazilian date format, `€`-prefixed money strings). `WeeklySummaryService` will depend on `DailySummaryService`'s existing `_parse_row`/`_normalize_date`/`_parse_money` static helpers (or an extracted shared helper module if duplication would otherwise occur) instead of re-implementing parsing.

4. **Fixed in-code category → emoji map with a default fallback.**
   Rationale: No existing emoji mapping exists in the codebase. A small `dict[str, str]` constant covering known categories (e.g. Supermercado, Commuting/Transporte, Compras diversas, Extras, Saúde) with a sensible default emoji (e.g. `🔹`) for unmapped categories keeps the formatter simple and testable without adding configuration surface.

5. **New `WeeklySummaryScheduler` class instead of parameterizing `DailySummaryScheduler`.**
   Rationale: Following the existing pattern (`DailySummaryScheduler` wraps `RecurringJobScheduler(DailyRecurrence(...))`), a parallel `WeeklySummaryScheduler` wraps `RecurringJobScheduler(WeeklyRecurrence(...))`. This keeps each scheduler small, testable in isolation, and consistent with the codebase's existing convention rather than introducing a generic parameterized scheduler now.

## Risks / Trade-offs

- [Risk] Category names in the sheet may not exactly match the fixed emoji map keys (casing/accents/typos). → Mitigation: Normalize category text (trim + case-insensitive lookup) before matching, and fall back to a default emoji rather than failing.
- [Risk] Running the aggregation window off the job's execution date could produce an off-by-one day if the scheduler fires slightly early/late. → Mitigation: Compute the window from the injected/reference date consistently, and cover boundary dates (window start/end) with unit tests.
- [Risk] A user with zero transactions in the week yields an empty message. → Mitigation: Mirror `DailySummaryMessageFormatter`'s empty-state message with a weekly-appropriate "no expenses this week" fallback.
- [Risk] Two schedulers (daily + weekly) running as separate background threads increases the chance of overlapping Telegram sends if both fire near the same time. → Mitigation: Each job already isolates per-user errors and sends messages independently; no shared mutable state between jobs, so this is a non-issue beyond normal logging noise.

## Migration Plan

1. Add `WeeklySummaryService` (category aggregation + trailing-week filtering) and `WeeklySummaryMessageFormatter` (category-grouped message with emoji map).
2. Add `WeeklySummaryJob` mirroring `DailySummaryJob`'s structure (`run_for_spreadsheet`, `run_for_user`, `run_all_users`, `sendMessage`), reusing `TelegramAdapterService` and the existing `TelegramService` wrapper.
3. Add `WeeklySummaryScheduler` wrapping `RecurringJobScheduler(WeeklyRecurrence(weekday=6, trigger_time=time(21, 0)))` (Sunday = weekday 6 per `WeeklyRecurrence`'s Monday=0 convention).
4. Register the weekly scheduler in `main.py` alongside the daily scheduler.
5. Add unit tests for date-window filtering, category aggregation, message formatting, and scheduler trigger-time computation.

## Open Questions

- Whether "week" should always mean Sunday-Saturday regardless of when the job is deployed/triggered, or whether it should be configurable per user/timezone in the future.
- Whether categories not covered by the fixed emoji map should be logged for future map updates.
