## 1. Recurrence rules

- [x] 1.1 Create `recurrence_rule.py` defining a `RecurrenceRule` protocol/ABC with `next_run(after: datetime) -> datetime`.
- [x] 1.2 Implement `DailyRecurrence(trigger_time: time)` with `next_run` logic ported from `DailySummaryScheduler._compute_seconds_until_next_run`.
- [x] 1.3 Implement `WeeklyRecurrence(weekday: int, trigger_time: time)` with `next_run` logic handling "today is the target weekday but time already passed".
- [x] 1.4 Implement `MonthlyRecurrence(day_of_month: int, trigger_time: time)` with `next_run` logic handling month rollover and short months (e.g. day 31 in a 30-day month).
- [x] 1.5 Add unit tests for each rule covering: before-trigger-time-today, after-trigger-time-today, and cadence-specific boundary cases (week rollover, month rollover/short months).

## 2. Generic recurring job scheduler

- [x] 2.1 Create `RecurringJobScheduler` that takes a `RecurrenceRule` and callback, computes sleep duration from `rule.next_run(datetime.now())`, sleeps, invokes the callback, and repeats indefinitely in a daemon thread (extracted from `DailySummaryScheduler._run_loop`/`start`).
- [x] 2.2 Ensure callback exceptions are caught and logged per iteration without stopping the loop (mirroring existing `DailySummaryScheduler` behavior).
- [x] 2.3 Add unit tests for `RecurringJobScheduler` covering delay computation from a rule and continued scheduling after a callback exception.

## 3. Refactor DailySummaryScheduler onto the shared architecture

- [x] 3.1 Update `DailySummaryScheduler` to build a `DailyRecurrence` internally and delegate `start`/`schedule` to a `RecurringJobScheduler`, keeping its constructor signature (`trigger_time: time | None = None`) unchanged.
- [x] 3.2 Keep `_compute_seconds_until_next_run` as a thin delegate to `DailyRecurrence.next_run` so the existing test (`test_daily_summary_scheduler_uses_8pm_target_time`) passes unmodified.
- [x] 3.3 Re-run `tests/unit/test_daily_summary_job.py` and any scheduler tests to confirm no regression in the daily summary flow or `main.py` wiring.

## 4. Verification

- [x] 4.1 Run the full unit test suite and confirm all new and existing tests pass.
- [x] 4.2 Manually confirm `main.py` still starts the daily summary scheduler without changes to its call site.
