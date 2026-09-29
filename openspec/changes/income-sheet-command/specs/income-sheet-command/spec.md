# Spec Delta

## Purpose

Allow mapped Telegram users to read and record income in their own `Rendimentos` worksheet tab through a discoverable assistant command.

## ADDED Requirements

### Requirement: Income records can be read from the Rendimentos tab
The system SHALL read income records from columns B through E of the `Rendimentos` tab in the spreadsheet mapped to the requesting Telegram user.

#### Scenario: A mapped user reads income records
- **WHEN** a mapped user invokes the income workflow
- **THEN** the system retrieves that user's records from `Rendimentos!B:E`

#### Scenario: An unmapped user requests income records
- **WHEN** a user without a spreadsheet mapping invokes the income workflow
- **THEN** the system informs the user that a spreadsheet registration is required and does not access another user's spreadsheet

### Requirement: Income records can be added to the Rendimentos tab
The system SHALL append a new income record to columns B through E of the mapped user's `Rendimentos` tab without overwriting existing records.

#### Scenario: A valid income record is submitted
- **WHEN** the income workflow receives the required income values for a mapped user
- **THEN** the system appends one new record to the next available row in `Rendimentos!B:E` and confirms the result

#### Scenario: The income record cannot be stored
- **WHEN** the spreadsheet service rejects or cannot complete an income write
- **THEN** the system reports that the income could not be recorded and does not report a successful write

### Requirement: Rendimentos command opens the income workflow
The system SHALL provide a `/rendimentos` Telegram command that routes the requesting mapped user to the income worksheet workflow.

#### Scenario: A user invokes the Rendimentos command
- **WHEN** a Telegram user sends `/rendimentos`
- **THEN** the assistant uses the `Rendimentos` tab for that user's income interactions

### Requirement: Help lists the Rendimentos command
The system SHALL include `/rendimentos` and its purpose in the response to the `/ajuda` command.

#### Scenario: A user requests help
- **WHEN** a Telegram user sends `/ajuda`
- **THEN** the response identifies `/rendimentos` as the command for viewing and recording income
