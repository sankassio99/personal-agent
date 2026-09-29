# Proposal

## Why

When users omit a category while recording an expense or income, the agent currently has no reliable source of valid choices. Reading the spreadsheet-maintained category lists lets the agent infer a valid category without inventing one.

## What Changes

- Add a Google Sheets tool that retrieves the available expense categories from `Sumário!B30:B42` and income categories from `Sumário!B49:B53` for the requesting user's mapped spreadsheet.
- Add agent instructions requiring category retrieval and inference whenever a user omits the category while adding an expense or income.
- Keep explicit user-provided categories unchanged and preserve user-to-spreadsheet isolation.

## Capabilities

### New Capabilities

- `available-categories-tool`: Retrieve spreadsheet-managed expense and income categories for agent-guided category inference.

### Modified Capabilities

- None.

## Impact

- Adds a Google Sheets read tool and makes it available to the finance agent.
- Updates expense and income agent instructions for incomplete category input.
- Reuses the existing Telegram user mapping and Google Sheets authentication configuration without adding dependencies.
