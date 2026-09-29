## Context

The expense workflow appends a row to the client's `Despesas` worksheet. `GoogleSheetsRepository` provides general sheet reads, and `TelegramService` provides message delivery. The category summary is in `'Sumário'!B27:F42`: column B contains category names, D the planned monthly budget, E the actual value, and F the difference.

## Goals / Non-Goals

**Goals:**
- After a successful expense write, retrieve the matching category's summary values for the client and calculate budget usage.
- Send a separate Telegram notification when actual usage is above 70% of planned budget, with a distinct alert when actual exceeds budget.
- Keep budget lookup or message delivery failures from changing the outcome of an already completed expense write.

**Non-Goals:**
- Change expense recording, budget configuration, or the spreadsheet layout.
- Proactively monitor spending outside the expense-entry flow.
- Notify when usage is at or below 70% of the budget.

## Decisions

1. **Run a notification service after `add_expense` succeeds.** It receives the client identifier and category only after the expense is saved, so a failed write cannot trigger an alert.

2. **Add a category-specific repository lookup.** The notification service resolves the client's spreadsheet using the existing client mapping, then asks a new `GoogleSheetsRepository` method for the requested category. The method reads the summary range and matches the category in column B, returning its planned value from D, actual value from E, and difference from F. This keeps Google Sheets access and row interpretation in the repository rather than duplicating it in the service.

3. **Calculate percentage and send via the existing Telegram transport.** The notification service calculates `actual / planned * 100`, formats the qualifying notification, and calls `TelegramService.send_message` with the client's identifier. The separate message keeps the expense confirmation flow independent.

4. **Use mutually exclusive alert levels.** If spend is greater than the budget, show the over-budget alert. Otherwise, if spend is greater than 70% of budget, show the near-limit notice. The over-budget state takes precedence so a user does not receive both messages.

5. **Treat notification as a best-effort follow-up.** Missing, invalid, or unreadable budget data must not undo the expense. Log lookup and delivery failures and do not send a fabricated status.

## Risks / Trade-offs

- [A stale summary formula could return an outdated actual value] → Read the summary after the successful write and verify the Sheets formula updates as expected; do not silently substitute a different calculation.
- [A client or category lookup could select incorrect spreadsheet data] → Resolve the spreadsheet from the client identifier, match the category by column B, and test client isolation and missing categories.
- [Zero, malformed, or missing budgets make percentage calculations invalid] → Skip notifications for missing, non-numeric, or non-positive planned values and cover these cases in tests.
- [Telegram delivery can fail after an expense has been saved] → Log delivery failure without changing the expense-write result.

## Migration Plan

No data migration is expected. Deploy the repository lookup and notification service against existing client spreadsheets. Roll back by removing the post-write notification call while leaving expense recording unchanged.

## Open Questions

- Confirm the desired user-facing language and currency formatting for the separate Telegram notification.