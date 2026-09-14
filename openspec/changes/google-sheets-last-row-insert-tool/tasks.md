## 1. Tool Contract and Wiring

- [x] 1.1 Keep the created `add_expense` tool as the designated Google Sheets expense append contract.
- [x] 1.2 Update the adapter or handler flow so the active Telegram user’s spreadsheet context is resolved before the tool is invoked.

## 2. Google Sheets Context and Safety

- [x] 2.1 Ensure the configured `SHEET_NAME` and spreadsheet id remain compatible with the user-to-spreadsheet mapping flow.
- [x] 2.2 Add a regression test that confirms the append tool path is used to write the value payload through the existing Sheets API call rather than a separate row-state resolver.

## 3. Validation and Error Handling

- [x] 3.1 Surface a clear error when the spreadsheet id cannot be resolved for a Telegram user.
- [x] 3.2 Confirm the created `add_expense` tool continues to place the expense in the next available row through `INSERT_ROWS` append semantics.
