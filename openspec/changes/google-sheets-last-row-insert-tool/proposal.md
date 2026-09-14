## Why

The repository already contains an `add_expense` Google Sheets tool in the finance assistant agent infrastructure, but the planning artifacts should explicitly describe that the intended implementation path is to use that tool and not invent a separate row-discovery workflow. The existing tool already calls the Sheets `append` API with a user-entered range and therefore writes the expense into the next available line automatically when the spreadsheet context is correctly resolved.

## What Changes

- Align the change plan with the created `add_expense` tool in the agent infrastructure, using it as the canonical entry point for expense insertion.
- Document that the spreadsheet identity and sheet configuration should come from the previously established user-to-spreadsheet routing and sheet-name context rather than from a hard-coded line selection.
- Keep the planned implementation focused on wiring the existing Google Sheets append tool through the repository and adapter flow instead of introducing a separate low-level row look-up helper.

## Capabilities

### New Capabilities
- `google-sheets-add-expense-tool`: Provide a reusable capability that uses the created `add_expense` tool to append expense rows via Google Sheets API with `append` semantics.

### Modified Capabilities
- None.

## Impact

- Affects the Google Sheets infrastructure and the agent tool entry in the finance assistant codebase.
- Uses the existing `add_expense` tool contract in the infrastructure agent layer and ties it back to the user’s spreadsheet mapping context.
- Keeps the implementation centered on the API-driven append path instead of introducing an alternative manual “last row + next row” workflow.
