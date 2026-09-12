## Why

The repository currently has a basic finance assistant project skeleton, but it does not yet include a Telegram bot message flow. A first working bot interaction should demonstrate a real Telegram message receive and reply path using the `python-telegram-bot` package and a static response.

## What Changes

- Add a Telegram bot command or message handler that receives messages from the Telegram bot API.
- Send a fixed, static text response back to the same chat when the bot receives a user message.
- Wire the repository to the `python-telegram-bot` dependency and demonstrate the minimal bot configuration pattern.

## Capabilities

### New Capabilities
- `telegram-static-response`: Introduce a Telegram handler that receives a message and replies with a static response using `python-telegram-bot`.

### Modified Capabilities
- None.

## Impact

This change introduces a lightweight Telegram integration path in the project, adds the `python-telegram-bot` dependency, and establishes the first end-to-end message receive/reply sample that can be expanded into the finance assistant workflow.
