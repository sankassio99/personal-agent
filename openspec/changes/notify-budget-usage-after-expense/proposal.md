## Why

Users currently receive no separate notification when a recorded expense brings a category close to or above its monthly budget. Notifying the client after the expense is saved gives them timely visibility into category-level budget usage.

## What Changes

- After a successful expense write, use the client identifier and expense category to retrieve the matching row from the client's `Sumário` worksheet.
- Add a category-specific lookup method to `GoogleSheetsRepository`; the summary row uses column B for category, D for planned budget, E for actual value, and F for difference, with category rows beginning at row 27.
- Add a budget notification service that calculates usage as actual divided by planned budget, multiplied by 100.
- Send a separate near-limit message when usage is above 70% and at or below 100%, and a distinct over-budget alert when usage exceeds 100%, through `TelegramService`.
- Do not send a budget notification for unavailable or invalid budget data, and do not change the result of an expense that was already recorded.

## Capabilities

### New Capabilities
- `expense-budget-alerts`: Retrieve client-scoped category budget data and send a separate Telegram notification when monthly usage is above 70% or exceeds the planned budget.

### Modified Capabilities
- None

## Impact

- Affects the expense-entry workflow, a budget notification service, `GoogleSheetsRepository`, and Telegram delivery through `TelegramService`.
- Reuses the existing client-to-spreadsheet mapping and Google Sheets authentication; no new dependency or worksheet migration is expected.