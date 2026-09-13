## 1. Wire the Telegram reply path

- [x] 1.1 Update the Telegram handler to send the finance agent reply using Telegram HTML parse mode instead of Markdown.
- [x] 1.2 Add a formatter/normalization utility that converts the finance reply from Markdown-style text into a Telegram-safe HTML representation.

## 2. Dependency and validation updates

- [x] 2.1 Add the Markdown parser / HTML conversion dependency needed for the converter.
- [x] 2.2 Verify that outbound responses are escaped safely and that the bot replies with HTML parse mode.
