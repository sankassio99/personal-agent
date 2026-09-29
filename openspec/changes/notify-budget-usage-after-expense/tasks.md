## 1. Budget Data and Calculation

- [x] 1.1 Add a category-specific `GoogleSheetsRepository` method that reads the client's `Sumário` category row and returns columns B (category), D (planned), E (actual), and F (difference).
- [x] 1.2 Add repository tests for category matching, returned column values, missing categories, and client spreadsheet isolation.
- [x] 1.3 Implement a budget notification service that accepts the client identifier and category, resolves the client's spreadsheet, and calculates usage as actual divided by planned budget times 100.
- [x] 1.4 Add service tests for invalid or non-positive budgets, the exact 70% and 100% boundaries, and over-budget alert precedence.

## 2. Expense and Telegram Integration

- [x] 2.1 Use `TelegramService.send_message` to send the qualifying near-limit or over-budget notification separately to the client.
- [x] 2.2 Invoke the notification service only after `add_expense` succeeds; keep a budget lookup or Telegram delivery failure from changing the recorded expense result and log the failure.
- [x] 2.3 Add integration tests for no notification at or below 70%, a near-limit message above 70% through 100%, an over-budget alert above 100%, and no alert when expense recording fails.

## 3. Expense Workflow and Regression Verification

- [x] 3.1 Wire the budget notification service into the successful expense workflow with the client identifier and category, without moving the notification into the agent's expense confirmation text.
- [x] 3.2 Run focused repository, notification service, expense workflow, and agent tests to verify existing expense recording and client spreadsheet isolation remain unchanged.