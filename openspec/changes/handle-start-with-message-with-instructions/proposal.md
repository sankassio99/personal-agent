## Why

The Telegram bot entry flow currently has a `handle_start` callback and a text-message handler, but the repository does not yet define a start-command experience that explains the Telegram user and provides a friendly onboarding message. The requested change introduces a clearer `/start` flow that identifies the Telegram user context and tells the user how to register the spreadsheet workflow and receive instructions.

## What Changes

- Add a dedicated `/start` command experience for the Telegram adapter that responds with a useful message.
- Provide instructions in the reply that tell the user how to proceed when no spreadsheet mapping exists.
- Keep the start message aligned with the existing finance assistant Telegram handler architecture.

## Capabilities

### New Capabilities
- `handle-start-message`: Provide a Telegram `/start` response with registration and contact instructions for the user.

### Modified Capabilities
- None.

## Impact

Affected areas include the Telegram application handler flow and the repository’s existing conversation bootstrap path in the `src/finance_assistant/application/handlers/` layer. The change introduces a user-facing onboarding message without replacing the existing Telegram or FinanceAgent message pipeline.
