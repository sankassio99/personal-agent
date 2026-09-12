## 1. Configuration and Google Sheets Tool Integration

- [ ] 1.1 Extend application settings and environment documentation with the Google Sheets credentials, spreadsheet, OAuth/service-account, and range configuration required by the Agno GoogleSheetsTools direct route.
- [ ] 1.2 Implement the Google Sheets service/tool adapter directly against the Agno GoogleSheetsTools Google Sheets integration while keeping the existing Google Sheets client and repository abstractions available for explicit repository seams and test doubles.

## 2. Telegram Finance Routing

- [ ] 2.1 Add a dedicated `/finance` prefix parser and handler that supports trimmed, case-insensitive keyword matching and rejects empty requests.
- [ ] 2.2 Register the finance handler before the generic text handler and route valid payloads to the direct Google Sheets service adapter.
- [ ] 2.3 Preserve generic response-agent handling for non-`/finance` text and surface finance routing failures without fallback.

## 3. Verification and Documentation

- [ ] 3.1 Add unit tests covering valid routing, case-insensitive matching, token boundaries, bare-keyword errors, ordinary messages, and Google Sheets tool failures.
- [ ] 3.2 Add unit tests covering valid and missing Google Sheets configuration plus spreadsheet operation errors using mocked Google Sheets dependencies.
- [ ] 3.3 Update the README with Google Sheets tool setup, required environment values, startup instructions, and `/finance` usage examples.
- [ ] 3.4 Run the existing test suite and validate the OpenSpec scenarios against the implemented behavior.
