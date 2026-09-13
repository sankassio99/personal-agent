## ADDED Requirements

### Requirement: Telegram start command sends onboarding instruction message
The system SHALL reply to a Telegram `/start` command with a short onboarding message describing how the user should contact the administrator and provide the Telegram user id and email address needed to create a Google Sheets spreadsheet.

#### Scenario: User enters /start
- **WHEN** a Telegram user sends the `/start` command
- **THEN** the system SHALL reply with a message that includes a contact handle for the administrator and a request to send the Telegram user id and email address for spreadsheet creation
