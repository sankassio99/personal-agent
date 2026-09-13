## 1. Service Skeleton

- [x] 1.1 Create an application service module named `TelegramAdapterService` under the finance assistant application service boundary.
- [x] 1.2 Expose a class or function that accepts a Telegram user id and returns the user’s spreadsheet id.

## 2. User-to-Spreadsheet Mapping

- [x] 2.1 Create a dictionary structure that maps Telegram `user_id` keys to spreadsheet `spreadsheet_id` values.
- [x] 2.2 Add a resolver that safely treats an unknown Telegram id as an unregistered user scenario.

## 3. Telegram Handler Wiring

- [x] 3.1 Update the Telegram handler flow so it uses `TelegramAdapterService` rather than embedding a static spreadsheet id in the reply instruction string.
- [x] 3.2 Ensure the FinanceAgent is started with the spreadsheet id associated with the current user’s context.

## 4. Verification

- [x] 4.1 Add or update a test that confirms the adapter service can return a valid spreadsheet id mapping for a known Telegram user.
- [x] 4.2 Add or update a regression test that confirms an unknown Telegram user id degrades safely.
