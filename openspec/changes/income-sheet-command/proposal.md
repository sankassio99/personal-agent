# Proposal

## Why

The assistant currently records and reads expenses but does not provide an equivalent, guided workflow for income. Users need to access the `Rendimentos` worksheet tab and manage income entries from Telegram without manually opening the spreadsheet.

## What Changes

- Add an income-specific Google Sheets tool that reads and appends entries in the `Rendimentos` tab, using columns B through E and the existing service-account authentication path.
- Add a `/rendimentos` Telegram command that resolves the requesting user's spreadsheet and presents the income workflow.
- Update `/ajuda` so users can discover the `/rendimentos` command.
- Preserve user-to-spreadsheet isolation and existing expense behavior.

## Capabilities

### New Capabilities

- `income-sheet-command`: Read and append income records in the `Rendimentos` worksheet tab through a Telegram command.

### Modified Capabilities

- None.

## Impact

- Affects Telegram command routing and help output.
- Adds Google Sheets read/write tooling for income records and prompt or agent wiring for the income workflow.
- Reuses the existing Telegram user mapping and Google Sheets service-account configuration; no new external dependency is expected.
