## Why

The finance assistant already reads expense data from Google Sheets and exposes user-scoped spreadsheet lookups, but it does not yet provide a scheduled daily summary flow. A recurring 8:00 PM job would give users a consistent, date-aware summary of their expenses without requiring a manual prompt each day.

## What Changes

- Add a scheduled daily job that triggers every day at 20:00 local time.
- Introduce a repository-backed fetch path that reads spreadsheet rows through `get_sheet(spreadsheet_id, sheet_name, filter)`.
- Add a dedicated daily summary service that filters records for the current date and returns a structured payload.
- Return summary rows as normalized objects containing `date`, `value`, `description`, and `category`.
- Keep the default expense and Telegram flows unchanged unless they explicitly opt into the summary job.

## Capabilities

### New Capabilities
- `daily-summary-job`: Add a scheduled daily summary capability that reads a user’s sheet data, filters it by the current date, and returns a structured summary payload.

### Modified Capabilities
- `google-sheets-tool`: Extend the repository/service contract with a read-only filtered lookup pattern that supports the daily summary use case without changing existing write operations.

## Impact

- Affects the finance assistant’s background scheduling layer and service composition in the application runtime.
- Introduces a repository call pattern around Google Sheets read access for date-filtered summary retrieval.
- Adds a structured output contract consumed by the scheduler or downstream API layer; no user-facing Telegram command changes are required unless a delivery channel is added later.
