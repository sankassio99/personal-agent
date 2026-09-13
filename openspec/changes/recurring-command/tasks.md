## 1. Bot and command registration

- [x] 1.1 Register a Telegram `CommandHandler("recurring", handle_recurring)` in the bot builder alongside the existing start command registration.
- [x] 1.2 Import the new command callback into the bot module so the command is reachable from the app lifecycle.

## 2. Handler command routing

- [x] 2.1 Add `handle_recurring` in the Telegram handler module and route the command to the centralized dispatcher.
- [x] 2.2 Supply the recurring worksheet range `"'Recorrentes'!A1:E50"` to the shared financial agent dispatch path for this command.

## 3. Verification

- [x] 3.1 Add or update a regression test that confirms the recurring handler passes the requested `spreadsheet_range` override.
- [x] 3.2 Re-run the existing unit tests that cover the Telegram handler fallback, registration gate, and HTML conversion path.
