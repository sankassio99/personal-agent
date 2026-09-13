## ADDED Requirements

### Requirement: Telegram HTML reply conversion
The system SHALL convert Markdown-style agent responses into a Telegram-safe HTML reply payload before sending the message through the Telegram handler.

#### Scenario: Markdown-like response becomes HTML-safe Telegram reply
- **WHEN** the finance assistant generates a response from the message adapter
- **THEN** the Telegram handler SHALL transform that response into an HTML-safe payload and send it with HTML parse mode

### Requirement: Telegram handler response formatting
The system SHALL use Telegram HTML parse mode in the reply path instead of Markdown parse mode for the assistant message handler.

#### Scenario: Telegram sends HTML reply
- **WHEN** a user message reaches the Telegram handler
- **THEN** the handler SHALL send the finance agent response using Telegram HTML parse mode
