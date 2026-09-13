## Why

The finance assistant currently has a Telegram handler that starts a static, shared agent instruction string with a hard-coded Google Sheet example. That design cannot identify the Telegram user who is sending the message or choose the spreadsheet that belongs to that user’s account. A per-user Telegram adapter layer is needed so the correct spreadsheet identifier can be resolved before the FinanceAgent starts.

## What Changes

- Add an application service named `TelegramAdapterService` that owns Telegram user identification and spreadsheet resolution.
- Introduce a dictionary-style mapping from Telegram user id to the spreadsheet id associated with that Telegram account.
- Ensure the FinanceAgent initialization path can look up the right spreadsheet id for the conversation participant instead of relying on a static, shared sample sheet.
- Keep the adapter service scoped to the existing Telegram event and application handler architecture in the repository.

## Capabilities

### New Capabilities
- `telegram-adapter-service`: Provide a reusable application service that discovers the Telegram user, resolves the matching spreadsheet id, and prepares the correct account context for the FinanceAgent.

### Modified Capabilities
- None.

## Impact

Affected areas include the Telegram application handler flow, the finance assistant infrastructure settings and environment configuration, and the repository’s existing conversation bootstrap path in the `src/finance_assistant/application/handlers/` and `src/finance_assistant/infrastructure/` layers. The change introduces an account-routing abstraction but does not replace the existing Telegram or FinanceAgent message pipeline.
