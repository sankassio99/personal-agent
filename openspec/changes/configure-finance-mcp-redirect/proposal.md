## Why

The finance assistant currently treats all Telegram text as ordinary agent input, so users have no reliable way to request spreadsheet-backed finance operations. A `/finance` keyword should provide an explicit entry point that routes the request through a direct Agno GoogleSheetsTools Google Sheets adapter, matching the Google Sheets toolkit usage described in the Agno docs.

## What Changes

- Remove the separate Google Spreadsheet MCP server planning from the change and wire the finance flow to a direct Agno GoogleSheetsTools Google Sheets service boundary.
- Detect messages beginning with the `/finance` keyword and route their payload directly to the Google Sheets tool adapter without falling through to the generic response agent.
- Preserve existing handling for non-`/finance` messages and Telegram commands.
- Surface configuration and routing errors instead of silently falling back to a generic response.
- Add tests and documentation for configuring the Google Sheets tool integration and using the `/finance` route.

## Capabilities

### New Capabilities

- `finance-keyword-routing`: Route Telegram messages with the `/finance` keyword to the Agno Google Sheets tool integration.

### Modified Capabilities

<!-- No existing OpenSpec capabilities are present; this change introduces the finance routing capability above. -->

## Impact

- Telegram message handlers and bot registration in `src/finance_assistant/telegram/`.
- Google Sheets tool adapter and application configuration in the repo.
- Environment variable documentation and automated tests.
