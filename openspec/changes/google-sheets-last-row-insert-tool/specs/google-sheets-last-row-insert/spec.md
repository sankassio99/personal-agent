## ADDED Requirements

### Requirement: Google Sheets add_expense tool appends an expense using the worksheet append API
The system SHALL provide and use the created `add_expense` tool in the finance assistant infrastructure so that an expense object is written to the configured Google Sheets spreadsheet through the `append` API semantics and the `Despesas` worksheet range.

#### Scenario: Expense is appended to the sheet
- **WHEN** the `add_expense` tool receives a valid date, amount, description, and category
- **THEN** the tool SHALL send the values payload to the Google Sheets `spreadsheets().values().append()` API with `valueInputOption="USER_ENTERED"` and `insertDataOption="INSERT_ROWS"`

#### Scenario: Tool writes to the next available line
- **WHEN** the call uses the configured worksheet and spreadsheet context
- **THEN** the Google Sheets API SHALL place the expense in the next available row automatically, consistent with the tool’s existing `append` contract

### Requirement: Spreadsheet context is resolved before the created tool is invoked
The system SHALL ensure that the spreadsheet id used by the `add_expense` tool is sourced from the project’s Telegram adapter or spreadsheet mapping flow rather than from a static hard-coded value in the tool.

#### Scenario: Spreadsheet resolution succeeds
- **WHEN** the Telegram adapter resolves the active user’s spreadsheet id
- **THEN** the `add_expense` invocation SHALL receive the correct spreadsheet context and write the expense to that workbook

#### Scenario: Spreadsheet resolution fails
- **WHEN** no spreadsheet id can be determined for the user
- **THEN** the system SHALL return a clear routing or configuration error instead of writing to an arbitrary spreadsheet target
