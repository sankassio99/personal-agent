## Why

The finance assistant currently treats all Telegram text as ordinary agent input, so users have no reliable way to request spreadsheet-backed finance operations. A `/finance` keyword should provide an explicit entry point that routes the request through the Google Spreadsheet MCP integration.

## What Changes

- Add Google Spreadsheet MCP server setup and configuration to the finance assistant.
- Detect messages beginning with the `/finance` keyword and route their payload to the Google Spreadsheet MCP path.
- Preserve existing handling for non-`/finance` messages and Telegram commands.
- Surface configuration and routing errors instead of silently falling back to a generic response.
- Add tests and documentation for configuring the MCP server and using the `/finance` route.

## Capabilities

### New Capabilities

- `google-spreadsheet-mcp`: Configure and expose the Google Spreadsheet MCP server and its finance-oriented tool path.
- `finance-keyword-routing`: Route Telegram messages with the `/finance` keyword to the Google Spreadsheet MCP integration.

### Modified Capabilities

<!-- No existing OpenSpec capabilities are present; this change introduces the two capabilities above. -->

## Impact

- Telegram message handlers and bot registration in `src/finance_assistant/telegram/`.
- MCP server and tool modules in `src/finance_assistant/mcp/`.
- Google Sheets infrastructure and application configuration.
- Environment variable documentation and automated tests.
