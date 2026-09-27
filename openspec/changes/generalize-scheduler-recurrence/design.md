## Context

Today, `DailySummaryScheduler` (in `daily_summary_scheduler.py`) hardcodes a single recurrence: it computes the seconds until the next occurrence of a fixed `time` (default 20:00), sleeps, invokes a callback, and repeats forever in a daemon thread. `main.py` wires exactly one instance of this scheduler to `job.run_all_users()`.

There is no shared vocabulary for "run every day", "run every week on Monday", "run on the 1st of the month", etc. Any new cadence would require copying the sleep/loop/exception-handling logic in `_run_loop` and reimplementing "compute next run" math from scratch. This proposal generalizes the scheduling primitive while keeping the existing daily behavior (and its public API) intact.

## Goals / Non-Goals

**Goals:**
- Define a small `RecurrenceRule` interface responsible only for computing the next run `datetime` given a reference `datetime`.
- Provide concrete rules for daily, weekly, and monthly cadences, plus a straightforward extension point for custom cadences (e.g. "every N hours", "every weekday").
- Provide one generic `RecurringJobScheduler` that owns the sleep/execute/reschedule loop and daemon-thread lifecycle, parameterized by a `RecurrenceRule` and a callback.
- Let `main.py` (or any future caller) register multiple independent recurring jobs, each with its own rule and callback.
- Preserve `DailySummaryScheduler`'s existing public surface (`start(callback)`, `schedule(callback)`, constructor accepting `trigger_time`) so `main.py` and existing tests keep working without changes, by having it delegate to the new architecture internally.

**Non-Goals:**
- Building a full cron-expression parser or adopting a third-party scheduling library (e.g. APScheduler). The recurrence rules stay simple, explicit Python classes.
- Changing what the daily summary job does (fetching, filtering, formatting, sending) — only how its trigger is computed and looped.
- Persisting schedules across process restarts, handling missed runs, or distributed/multi-process scheduling.
- Timezone-aware scheduling beyond what the current implementation already does (naive local `datetime`).

## Decisions

1. **Separate "when to run next" from "how to loop and execute".**
   Introduce `RecurrenceRule` (a `Protocol`/ABC with `next_run(after: datetime) -> datetime`) implemented by `DailyRecurrence(trigger_time: time)`, `WeeklyRecurrence(weekday: int, trigger_time: time)`, and `MonthlyRecurrence(day_of_month: int, trigger_time: time)`. A separate `RecurringJobScheduler` takes a `RecurrenceRule` + callback and owns the `while True: sleep -> execute -> repeat` loop, mirroring the current `_run_loop`/`start` structure in `DailySummaryScheduler`.

   Rationale: This mirrors the Strategy pattern — the loop/threading/error-handling code (currently duplicated per cadence if copy-pasted) is written once, and each cadence is a small, independently testable value object exposing one pure function (`next_run`). This is the same "isolate the trigger calculation from the callback" principle already used in the daily-summary-job design (`_compute_seconds_until_next_run` is already isolated and unit-tested).

   Alternatives considered:
   - *Adopt APScheduler*: rejected for now (Non-Goal) to avoid a new dependency and keep the existing lightweight thread-based approach; can be revisited later since the rule interface would still be compatible with wrapping a real scheduler.
   - *One scheduler subclass per cadence (`DailySummaryScheduler`, `WeeklySummaryScheduler`, ...)*: rejected because it duplicates the loop/thread/exception-handling logic that has nothing to do with cadence.

2. **Keep `DailyRecurrence.next_run` as the direct successor of `_compute_seconds_until_next_run`.**
   `DailyRecurrence.next_run(now)` returns the next `datetime` combining today's (or tomorrow's) date with `trigger_time`, using the same "next_run >= now" comparison already proven in the existing unit test (`test_daily_summary_scheduler_uses_8pm_target_time`). `RecurringJobScheduler` converts `next_run - now` into a sleep duration.

   Rationale: Minimizes behavior risk — the exact date-combination and rollover logic that is already tested moves almost unchanged into the new rule class, only returning a `datetime` instead of a second count.

3. **`DailySummaryScheduler` becomes a thin backward-compatible wrapper.**
   `DailySummaryScheduler.__init__(trigger_time=None)` builds a `DailyRecurrence(trigger_time or time(20, 0))` and stores it; `start(callback)`/`schedule(callback)` delegate to an internal `RecurringJobScheduler(self._recurrence, callback)`. The private `_compute_seconds_until_next_run` method is kept as a thin delegate to `self._recurrence.next_run(...)` (computing the seconds diff) so the existing unit test keeps passing unmodified.

   Rationale: Avoids a breaking change to `main.py` or existing callers while still centralizing the general loop in `RecurringJobScheduler`. New jobs (weekly/monthly) are added by constructing `RecurringJobScheduler(WeeklyRecurrence(...), callback)` directly rather than needing a new named wrapper class per cadence, though a thin wrapper can still be added later if ergonomics call for it.

4. **Multiple jobs run as independent daemon threads, each owning one `RecurringJobScheduler`.**
   `main.py` (or a future composition root) can call `.start()` on as many scheduler instances as needed; there is no shared registry or single-threaded loop multiplexing multiple rules.

   Rationale: Matches the current threading model (`threading.Thread(..., daemon=True)`) and keeps failure isolation per job — one job's exception (already caught and logged per iteration) cannot affect another job's loop.

## Risks / Trade-offs

- [Risk] Weekly/monthly `next_run` calculations are more error-prone (month-length edge cases, day-of-month > 28, DST-adjacent boundaries) than the existing daily case. → Mitigation: Unit test each rule's `next_run` independently with boundary cases (e.g. day 31 in a 30-day month, "today is trigger day but time already passed").
- [Risk] Introducing a generic scheduler could regress the already-tested daily behavior. → Mitigation: Keep `DailySummaryScheduler`'s public API and existing test (`test_daily_summary_scheduler_uses_8pm_target_time`) unchanged; add new tests for the generic scheduler and rules without deleting the old one.
- [Risk] Running many independent daemon threads scales poorly if the number of jobs grows large. → Mitigation: Out of scope for this change (Non-Goal); acceptable given the current single-digit number of scheduled jobs.

## Migration Plan

1. Add `RecurrenceRule` protocol/ABC and `DailyRecurrence`, `WeeklyRecurrence`, `MonthlyRecurrence` implementations with unit tests covering `next_run` edge cases.
2. Add `RecurringJobScheduler` implementing the generic sleep/execute/reschedule loop (extracted from `DailySummaryScheduler._run_loop`/`start`), with unit tests for delay computation and error isolation.
3. Refactor `DailySummaryScheduler` to compose `DailyRecurrence` + `RecurringJobScheduler` internally while keeping its constructor and public methods unchanged; re-run existing tests to confirm no regression.
4. Update `main.py` only if/when a second recurring job (weekly/monthly) is actually registered; no functional change required for this change to land.

## Open Questions

- Should `RecurringJobScheduler` support stopping/cancelling a running job (e.g. for tests or graceful shutdown), or is fire-and-forget daemon-thread behavior sufficient for now?
- Should weekly/monthly rules live in the same module as `DailyRecurrence`, or be split into per-cadence files under a new `scheduling/` package as the number of cadences grows?
