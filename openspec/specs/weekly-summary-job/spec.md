# weekly-summary-job Specification

## Purpose
TBD - created by archiving change weekly-summary-job. Update Purpose after archive.

## Requirements

### Requirement: Scheduled weekly summary job triggers weekly
The system SHALL schedule a background task that runs once a week (Sunday at 21:00 local time) and invokes the weekly summary flow for each configured finance data source.

#### Scenario: Schedule fires at the configured weekly time
- **WHEN** the scheduler reaches the configured weekly trigger (Sunday 21:00 in the application timezone)
- **THEN** the system SHALL call the weekly summary pipeline for every mapped Telegram user's spreadsheet.

#### Scenario: One user's failure does not block others
- **WHEN** the weekly summary pipeline raises an error while processing one user's spreadsheet
- **THEN** the system SHALL log the failure and continue processing the remaining mapped users.

### Requirement: Weekly summary service filters rows to the trailing 7-day window
The system SHALL provide a service that receives spreadsheet rows and returns only records whose date falls within the trailing 7-day window (previous Sunday through Saturday, inclusive) relative to the execution date.

#### Scenario: Rows inside the window are included
- **WHEN** the weekly summary service is invoked with a reference date and rows dated within the prior Sunday-to-Saturday range
- **THEN** it SHALL include those rows in the aggregation and exclude rows dated outside that range.

#### Scenario: Row dates use supported formats
- **WHEN** a row's date is expressed in ISO format or Brazilian `DD/MM/YYYY` format
- **THEN** the service SHALL normalize the date before applying the window filter, consistent with the existing daily summary date parsing.

### Requirement: Weekly summary service aggregates totals by category
The system SHALL aggregate the filtered rows' monetary values into a total per category, plus an overall grand total.

#### Scenario: Multiple rows in the same category are summed
- **WHEN** the trailing-week window contains more than one row for the same category
- **THEN** the service SHALL return a single entry for that category whose value is the sum of all matching rows.

#### Scenario: Grand total reflects all categories
- **WHEN** the weekly aggregation completes
- **THEN** the service SHALL return a grand total equal to the sum of every category's total.

### Requirement: Weekly summary message groups totals by category with emoji
The system SHALL format the weekly aggregation into a Telegram message that lists each category with an associated emoji and its total, followed by the week's date range and a grand total line.

#### Scenario: Message includes date range, category lines, and total
- **WHEN** the weekly summary message formatter is given category totals, a grand total, and the week's start/end dates
- **THEN** it SHALL produce a message showing the date range, one line per category with an emoji and formatted currency value, and a final total line.

#### Scenario: Unmapped category falls back to a default emoji
- **WHEN** a category has no entry in the known category-to-emoji mapping
- **THEN** the formatter SHALL render that category's line using a default fallback emoji instead of failing.

#### Scenario: No expenses in the week produces an empty-state message
- **WHEN** the weekly summary service returns no categories for the current window
- **THEN** the formatter SHALL produce a message indicating there were no recorded expenses for that week instead of an empty or malformed message.
