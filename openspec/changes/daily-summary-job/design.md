## Context

The repository already centralizes Google Sheets access through finance-service and agent layers, with spreadsheet identifiers resolved per Telegram user. The current implementation supports expense writes and raw reads, but there is no reusable daily aggregation path or scheduler boundary that can run automatically on a fixed time schedule.

This change introduces a background daily summary job that triggers at 20:00 and reads the user’s configured spreadsheet data through a repository abstraction. The scheduler should remain simple and testable, while the service logic is responsible for date filtering and serialization.

## Goals / Non-Goals

**Goals:**
- Run a daily job every day at 20:00.
- Read expense rows from the configured Google Sheet using a repository method shaped as `get_sheet(spreadsheet_id, sheet_name, filter)`.
- Return filtered records as structured dictionaries with `date`, `value`, `description`, and `category`.
- Keep the data extraction and transformation logic isolated from the scheduling trigger.

**Non-Goals:**
- Replacing the existing Telegram-driven workflow or realtime expense entry flow.
- Adding a new UI or user command for manual daily summary generation.
- Performing side-effect writes or updating sheet contents from the summary job.

## Decisions

1. Separate scheduler orchestration from summary logic.

   Rationale: The scheduler should only decide when to run; the service should own filtering and result shaping. This keeps the job testable and makes it easy to swap scheduler implementations later without changing the summary contract.

2. Use a Google Sheets repository interface with a `get_sheet` method and a `filter` argument.

   Rationale: The project already relies on a thin repository/service layer pattern and modeled data access around a spreadsheet ID and worksheet name. A filtered read aligns with the requirement and avoids embedding raw Google API logic inside the scheduler.

3. Normalize summary rows into a list of dictionaries.

   Rationale: The result must be structured and easy to serialize for downstream transport or logging. Returning a plain list of row objects with fixed keys keeps the contract explicit and stable.

4. Filter by the current date in the service layer rather than in the repository.

   Rationale: Repository access should remain generic, while the service owns business rules such as “only include rows that match today.” This preserves separation of concerns and keeps the filtering logic easier to unit test.

## Risks / Trade-offs

- [Risk] Sheets may contain mixed row formats or blank cells. → Mitigation: Normalize the filter logic to ignore rows that do not include the required date, description, and value fields.
- [Risk] Timezone mismatches may lead to summaries being generated for the wrong local day. → Mitigation: Use the application’s configured local timezone or the runtime host timezone consistently in the daily summary service.
- [Risk] A background job can silently fail if the scheduler is not registered or the service cannot resolve the spreadsheet id. → Mitigation: Add logs around scheduled execution and treat missing spreadsheet mappings as a clear error state.

## Migration Plan

1. Add the repository method and service contract for `get_sheet(spreadsheet_id, sheet_name, filter)`.
2. Implement the summary service with current-date filtering and normalization to the `date/value/description/category` object model.
3. Register the daily scheduler at 20:00 and connect it to the summary service.
4. Verify the flow with a focused unit test for date filtering and a scheduler smoke check for the cron trigger configuration.

## Open Questions

- Whether the summary should be emitted to Telegram, logs, or a future webhook/API endpoint.
- Whether the scheduler should be implemented with APScheduler, cron shell configuration, or a simple background process managed by the application runtime.
Should use https://scheduler.digon.io/pages/examples/quick_start.html
- Whether the job should process all configured users or a single spreadsheet source for the current user context.
