## Context

The repository currently dispatches Telegram messages through a centralized `handle_message` path that routes text and command-safe traffic to a shared `FinanceAgent` adapter. The base agent factory already accepts an optional `spreadsheet_range` override through the new command/refactor pattern introduced in the current work, but the bot registration does not register a `recurring` command and the command surface is still missing the dedicated range. The new requirement calls for a command-aware route that explicitly targets the recurring worksheet slice `"'Recorrentes'!A1:E50"`.

## Goals / Non-Goals

**Goals:**
- Register a `/recurring` Telegram command in the bot runner.
- Direct the recurring command through a dedicated handler that routes a range override into the shared finance agent factory.
- Preserve the default expense range for ordinary message traffic.

**Non-Goals:**
- Altering the finance agent’s model prompt or reply format.
- Replacing the existing message handler dispatch semantics for all text traffic.

## Decisions

1. Add a `CommandHandler("recurring", handle_recurring)` registration alongside the existing `/start` registration in the Telegram bot builder.

   Rationale: Telegram command registration is the canonical route for command-style intents and keeps `/recurring` independent from a plain text message parser.

2. Introduce a `handle_recurring` command callback in the Telegram application handlers. The command callback should delegate to the same `_dispatch_finance_reply` helper as the generic text flow, but pass the recurring range string `"'Recorrentes'!A1:E50"` as the selected `spreadsheet_range`.

   Rationale: The helper already centralizes spreadsheet mapping and message-to-agent dispatch, so reusing it keeps the code change minimal and testable.

3. Default the message path back to the expense range constant and only use the dedicated recurring range when the handler is explicitly triggered by the `/recurring` command.

   Rationale: This maintains the existing behavior for ad-hoc messages while enabling an opt-in command-specific range.

## Risks / Trade-offs

- [Risk] A command handler may produce an empty reply if the Telegram user is not yet registered. → Mitigation: Reuse the existing registration-check guard before constructing the agent.
- [Risk] Overloading one handler with command semantics can make the code less explicit. → Mitigation: Add a thin command-specific function and centralize the dispatch pipeline behind a single helper.
- [Risk] Unsupported worksheet names or missing range data. → Mitigation: Keep the code’s current error river through the `GoogleSheetsTools` layer and rely on the registered spreadsheet route to resolve the target sheet.

## Migration Plan

1. Register `/recurring` in the bot command stack and import the new `handle_recurring` callback.
2. Add the command callback to the Telegram application handler and route it to the shared dispatcher with the recurring range.
3. Verify no regression to the ordinary message text flow by keeping the fallback `EXPENSES_RANGE_NAME` constant.
4. Extend tests or add a small regression proof to cover the command range override path.

## Open Questions

- Whether other recurring commands should also be aggregated into a command-dispatch map rather than a sequence of singleton handler branches.
- Whether the recurring range should become a user-configurable setting instead of a fixed route constant.
