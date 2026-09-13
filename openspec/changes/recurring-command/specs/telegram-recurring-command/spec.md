## ADDED Requirements

### Requirement: Telegram recurring command response
The system SHALL recognize a Telegram `/recurring` command and route the request through the recurring command worksheet range `"'Recorrentes'!A1:E50"` when the user invokes the command.

#### Scenario: Recurring command arrives from Telegram
- **WHEN** a user sends the `/recurring` command to the assistant
- **THEN** the Telegram handler SHALL dispatch the request through a finance agent configured with the recurring worksheet range `"'Recorrentes'!A1:E50"`.

### Requirement: Base agent range override
The system SHALL allow an optional `spreadsheet_range` override to be passed to the reusable base agent factory so command handlers can choose a specific worksheet slice without changing the default range for ordinary messages.

#### Scenario: Recurring handler passes a range override
- **WHEN** the recurring Telegram command handler supplies `spreadsheet_range="'Recorrentes'!A1:E50"`
- **THEN** the agent factory SHALL create the `GoogleSheetsTools` object with that range while leaving the default fallback range unchanged when no override is passed.
