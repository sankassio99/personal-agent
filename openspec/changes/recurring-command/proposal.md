## Why

The Telegram workflow currently supports a fixed expense-oriented spreadsheet range and a summary command path that is routed through a separately configured range. Adding a dedicated recurring command should allow the expense assistant to answer recurring-transaction requests from a specific sheet window, `Recorrentes!A1:E50`, without overloading the general message handler or the existing expense range path.

## What Changes

- Introduce a new Telegram command named `/recurring` by registering a command endpoint in the bot runner and a matching command handler in the Telegram handler surface.
- Route the recurring command through a shared finance-agent execution path that applies the requested `GoogleSheetsTools` range override instead of the existing expense range.
- Use the sheet range `"'Recorrentes'!A1:E50"` as the recurring command’s active range for the command handler while keeping the normal message flow unchanged.

## Capabilities

### New Capabilities
- `telegram-recurring-command`: Add the capability to recognize a `recurring` Telegram command and direct the finance assistant to the `Recorrentes!A1:E50` worksheet range.

### Modified Capabilities
- `base-agent-factory`: Extend the reusable agent factory’s supported `spreadsheet_range` override to support a recurring command configuration path and keep the fallback sample range intact when no override is supplied.

## Impact

- Affects the Telegram command registration in the bot shell and the message/command dispatch path in the application handler.
- Affects the shared base agent factory responsible for constructing the Google Sheets tool with a chosen worksheet range.
- Keeps the response adapter and finance prompt contract stable while introducing a dedicated command-specific range.
