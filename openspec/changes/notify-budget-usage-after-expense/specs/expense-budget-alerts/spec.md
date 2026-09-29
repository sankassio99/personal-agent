## ADDED Requirements

### Requirement: Retrieve budget data for the client's category
The system SHALL use the client's identifier and expense category to retrieve the matching category row from the client's `Sumário` worksheet through a category-specific method on `GoogleSheetsRepository`. The row data SHALL use column B for the category name, column D for the planned monthly budget, column E for the actual value, and column F for the difference; category rows begin at row 27.

#### Scenario: Matching category data is retrieved
- **WHEN** the budget notification service requests budget data for a client and category
- **THEN** `GoogleSheetsRepository` SHALL return the planned, actual, and difference values from the matching category row in that client's spreadsheet

#### Scenario: Category is not present for the client
- **WHEN** the repository cannot find the requested category in the client's summary rows
- **THEN** it SHALL report that no matching budget data is available and SHALL NOT use another client's spreadsheet or another category's values

### Requirement: Calculate category budget usage and notify the client
After an expense is successfully added, the budget notification service SHALL calculate category budget usage as the actual value in column E divided by the planned monthly budget in column D, multiplied by 100. It SHALL send any resulting notification to the same client using `TelegramService.send_message` and the client's identifier.

#### Scenario: Expense is successfully added
- **WHEN** the expense write succeeds and the client has valid positive planned budget and actual values for the category
- **THEN** the budget notification service SHALL calculate the usage percentage and send a qualifying notification through `TelegramService` to that client

#### Scenario: Expense write fails
- **WHEN** the expense write fails
- **THEN** the budget notification service SHALL NOT send a budget notification for that expense

### Requirement: Notify when category budget usage is above 70 percent
The system SHALL send a near-limit notification when the actual value is greater than 70 percent of the planned monthly budget and does not exceed that budget. The message SHALL identify the category, actual value, planned budget, and percentage used.

#### Scenario: Actual value is above 70 percent and within budget
- **WHEN** the actual value is greater than 70 percent of the planned budget and less than or equal to the planned budget
- **THEN** the system SHALL send the client a near-limit notification with the actual value, planned budget, and percentage used

#### Scenario: Actual value is exactly 70 percent
- **WHEN** the actual value is exactly 70 percent of the planned budget
- **THEN** the system SHALL NOT send a near-limit notification

### Requirement: Alert when category actual value exceeds its budget
The system SHALL send an over-budget alert when the actual value in column E is greater than the planned budget in column D. This alert SHALL take precedence over the near-limit notification and identify the category, actual value, planned budget, and percentage used.

#### Scenario: Actual value exceeds the planned budget
- **WHEN** the actual value is greater than the planned monthly budget
- **THEN** the system SHALL send an over-budget alert through `TelegramService` and SHALL NOT send the near-limit notification

### Requirement: Handle unavailable budget data without misreporting
If category budget data cannot be retrieved or contains a missing, invalid, or non-positive planned budget, the system SHALL NOT calculate a percentage or send a budget notification. A budget lookup or notification failure SHALL NOT change whether the expense was successfully recorded.

#### Scenario: Budget data is unavailable after the expense is recorded
- **WHEN** the expense write succeeds but the repository cannot return valid category budget data
- **THEN** the system SHALL NOT send a budget notification and SHALL preserve the expense write result