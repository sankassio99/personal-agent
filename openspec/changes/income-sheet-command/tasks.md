# Tasks

## 1. Income Google Sheets tools

- [x] 1.1 Add an income read tool that resolves the requesting user's spreadsheet and reads `Rendimentos!B:E`; verify unit tests cover mapped and unmapped users.
- [x] 1.2 Add an income append tool that writes a complete income record to the next available row in `Rendimentos!B:E`; verify unit tests cover the request range, payload, and API failure propagation.
- [x] 1.3 Reuse the existing shared Google Sheets service-account builder for both income tools; verify tests confirm no OAuth browser or token-file path is invoked.

## 2. Telegram income workflow

- [x] 2.1 Add `/rendimentos` command routing that resolves the requesting user's spreadsheet and configures the assistant for `Rendimentos!B:E`; verify a handler test covers the range and mapped-user behavior.
- [x] 2.2 Add income-specific agent instructions and tool registration so reads and writes target `Rendimentos`; verify the constructed agent includes the income tools.
- [x] 2.3 Update `/ajuda` to document `/rendimentos` as the command for viewing and recording income; verify the help-message test asserts the command and description.

## 3. Integration validation

- [x] 3.1 Run the focused Telegram handler and income Google Sheets tool tests; verify they pass with `python3 -m pytest`.
- [x] 3.2 Validate the completed OpenSpec change with `openspec validate income-sheet-command --strict`; verify the command succeeds.
