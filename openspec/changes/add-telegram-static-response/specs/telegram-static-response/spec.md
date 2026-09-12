## ADDED Requirements

### Requirement: receive Telegram message and reply with static response
The system SHALL configure a Telegram bot using `python-telegram-bot` and SHALL send a static reply when a user message is received.

#### Scenario: successful static reply
- **WHEN** a user sends any text message to the bot
- **THEN** the bot SHALL reply with the configured static text response

### Requirement: bot configuration from environment
The system SHALL read the Telegram bot token from an environment or `.env` configuration source.

#### Scenario: token is configured
- **WHEN** the bot is started with a valid Telegram token
- **THEN** the Telegram application SHALL initialize and listen for incoming messages
