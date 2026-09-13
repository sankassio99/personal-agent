## 1. Telegram Start UX

- [ ] 1.1 Add a friendly `/start` handler response that explains the spreadsheet registration need.
- [ ] 1.2 Ensure the start reply mentions how to contact the administrator and what information to send.

## 2. Bot Wiring

- [ ] 2.1 Register the Telegram command route that invokes the start handler in the bot runner.
- [ ] 2.2 Keep the existing message flow using the adapter service for spreadsheet lookup.

## 3. Verification

- [ ] 3.1 Add or update a test that confirms the start command returns the requested instruction message.
- [ ] 3.2 Add or update a regression test that confirms that the no-spreadsheet fallback remains separate from FinanceAgent creation.
