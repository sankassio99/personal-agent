## ADDED Requirements

### Requirement: Telegram summary keyword response
The system SHALL recognize the `/summary` keyword in the Telegram conversation flow and route the message through a dedicated response path that uses a handler-provided spreadsheet range.

#### Scenario: Summary keyword arrives from Telegram
- **WHEN** a user sends the `/summary` keyword to the assistant
- **THEN** the Telegram handler SHALL construct the response using the configured summary spreadsheet range `'Sumário'!B27:F42` instead of the default expense range.

### Requirement: Base agent range override
The system SHALL allow the base agent `_create_agent` factory to accept a `spreadsheet_range` parameter from the handler and forward that override into the `GoogleSheetsTools` initialization.

#### Scenario: Handler passes a range override
- **WHEN** the Telegram handler supplies `spreadsheet_range='Sumário'!B27:F42` to the common agent factory
- **THEN** `_create_agent` SHALL build the `GoogleSheetsTools` object using that override while preserving the existing fallback range when no value is supplied.
