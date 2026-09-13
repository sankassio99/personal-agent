## Why

The Telegram finance assistant currently sends agent replies using Markdown parse mode, but the requested message flow needs HTML-safe rendering for richer Telegram formatting. A lightweight HTML reply path will let the assistant produce more consistent Telegram responses while keeping the backend response adapter simple.

## What Changes

- Change the Telegram message handler so replies are sent using Telegram HTML parse mode instead of Markdown.
- Introduce an HTML conversion step for the finance agent reply before the bot sends it to Telegram.
- Keep the existing finance agent response source intact, while normalizing markdown-derived output to Telegram HTML text.

## Capabilities

### New Capabilities
- `telegram-html-reply`: Introduce a Telegram response formatting capability that converts agent markdown-style output into Telegram HTML-compatible text.

### Modified Capabilities
- `telegram-response`: Update the existing Telegram response adapter requirement so that outbound replies support HTML parse mode.

## Impact

Affected code will include the Telegram integration handler and response formatting adapter in the finance assistant application layer. The dependency impact is limited to the Python Telegram library and an HTML conversion dependency for converting Markdown-like content into Telegram-compatible HTML.
