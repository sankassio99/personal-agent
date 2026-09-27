## ADDED Requirements

### Requirement: Recurrence rule computes the next run time
The system SHALL provide a `RecurrenceRule` abstraction exposing a `next_run(after: datetime) -> datetime` operation that, given a reference point in time, returns the next `datetime` at which the rule's cadence should trigger.

#### Scenario: Next run is requested before today's trigger time
- **WHEN** a recurrence rule's `next_run` is called with a reference time earlier than today's configured trigger time
- **THEN** the system SHALL return today's date combined with the configured trigger time.

#### Scenario: Next run is requested after today's trigger time
- **WHEN** a recurrence rule's `next_run` is called with a reference time later than today's configured trigger time
- **THEN** the system SHALL return the next valid occurrence strictly after the reference time (e.g. tomorrow for a daily rule, the following matching weekday for a weekly rule, or the following matching day-of-month for a monthly rule).

### Requirement: Daily recurrence rule
The system SHALL provide a `DailyRecurrence` rule that triggers once every day at a configurable `time`.

#### Scenario: Daily rule triggers at the configured time each day
- **WHEN** a `DailyRecurrence` configured with a given trigger time computes its next run from any reference `datetime`
- **THEN** the returned `datetime` SHALL fall on the same day (if the trigger time has not yet passed) or the following day (if it has), always at the configured trigger time.

### Requirement: Weekly recurrence rule
The system SHALL provide a `WeeklyRecurrence` rule that triggers once every week on a configurable weekday and time.

#### Scenario: Weekly rule triggers on the configured weekday
- **WHEN** a `WeeklyRecurrence` configured with a given weekday and trigger time computes its next run from any reference `datetime`
- **THEN** the returned `datetime` SHALL fall on the next occurrence of the configured weekday, at the configured trigger time, that is strictly after the reference `datetime`.

### Requirement: Monthly recurrence rule
The system SHALL provide a `MonthlyRecurrence` rule that triggers once every month on a configurable day-of-month and time.

#### Scenario: Monthly rule triggers on the configured day of month
- **WHEN** a `MonthlyRecurrence` configured with a given day-of-month and trigger time computes its next run from any reference `datetime`
- **THEN** the returned `datetime` SHALL fall on the next occurrence of the configured day-of-month, at the configured trigger time, that is strictly after the reference `datetime`, rolling over to the following month when the configured day has already passed or does not exist in the current month.

### Requirement: Generic recurring job scheduler
The system SHALL provide a `RecurringJobScheduler` that accepts any `RecurrenceRule` and a callback, and repeatedly waits until the rule's next run time before invoking the callback, indefinitely, in a background daemon thread.

#### Scenario: Scheduler invokes the callback at the computed time
- **WHEN** a `RecurringJobScheduler` is started with a given recurrence rule and callback
- **THEN** the system SHALL wait until the time computed by the rule's `next_run` and then invoke the callback, repeating this process indefinitely without blocking the caller's thread.

#### Scenario: Callback failure does not stop future runs
- **WHEN** the registered callback raises an exception during a scheduled execution
- **THEN** the system SHALL log the failure and continue scheduling subsequent runs according to the recurrence rule.

### Requirement: Multiple independent recurring jobs can be registered
The system SHALL support registering more than one recurring job simultaneously, each with its own recurrence rule and callback, without one job's execution or failure affecting another job's schedule.

#### Scenario: Two jobs with different cadences run independently
- **WHEN** a daily job and a weekly (or monthly) job are both started with independent `RecurringJobScheduler` instances
- **THEN** each job SHALL execute according to its own recurrence rule, and a failure or delay in one job SHALL NOT prevent or delay the other job's scheduled execution.
