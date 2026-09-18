## 1. Repository and service contract

- [ ] 1.1 Inspect the current Google Sheets integration surface and define the `get_sheet(spreadsheet_id, sheet_name, filter)` repository contract.
- [ ] 1.2 Add the daily summary service contract that accepts spreadsheet rows and returns only current-date entries.
- [ ] 1.3 Normalize the result to a structured payload with `date`, `value`, `description`, and `category` fields.

## 2. Scheduler integration

- [ ] 2.1 Choose the runtime scheduler mechanism for a daily 20:00 trigger and register it in the application startup path.
- [ ] 2.2 Connect the scheduler to the summary service so a trigger invokes the repository read and summary transformation flow.
- [ ] 2.3 Add logging around the scheduled execution and error handling for missing spreadsheet mappings or service failures.

## 3. Verification

- [ ] 3.1 Add a unit test covering date filtering for the current day.
- [ ] 3.2 Add a test confirming the structured output includes `date`, `value`, `description`, and `category`.
- [ ] 3.3 Run the focused test suite to verify the daily summary flow and scheduler wiring.
