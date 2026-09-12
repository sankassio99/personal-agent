## 1. Configuration and Google Spreadsheet MCP

- [ ] 1.1 Extend application settings and environment documentation with the Google Sheets credentials, spreadsheet, and MCP configuration required by the integration.
- [ ] 1.2 Implement the Google Spreadsheet MCP service/tool boundary using the existing Google Sheets client and repository abstractions.
- [ ] 1.3 Replace the placeholder MCP server entry point with startup, configuration validation, and explicit operational error handling.

## 2. Telegram Finance Routing

- [ ] 2.1 Add a dedicated `/finance` prefix parser and handler that supports trimmed, case-insensitive keyword matching and rejects empty requests.
- [ ] 2.2 Register the finance handler before the generic text handler and route valid payloads to the Google Spreadsheet MCP service.
- [ ] 2.3 Preserve generic response-agent handling for non-`/finance` text and surface finance routing failures without fallback.

## 3. Verification and Documentation

- [ ] 3.1 Add unit tests covering valid routing, case-insensitive matching, token boundaries, bare-keyword errors, ordinary messages, and MCP failures.
- [ ] 3.2 Add unit tests covering valid and missing MCP configuration plus spreadsheet operation errors using mocked Google Sheets dependencies.
- [ ] 3.3 Update the README with MCP setup, required environment values, startup instructions, and `/finance` usage examples.
- [ ] 3.4 Run the existing test suite and validate the OpenSpec scenarios against the implemented behavior.
