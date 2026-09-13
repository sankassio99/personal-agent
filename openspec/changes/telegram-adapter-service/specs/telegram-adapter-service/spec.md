## ADDED Requirements

### Requirement: TelegramAdapterService resolves a Telegram user to a spreadsheet id
The system SHALL provide an application service named `TelegramAdapterService` that receives a Telegram user id and returns the spreadsheet id that belongs to that user’s finance account context.

#### Scenario: Telegram user has a known spreadsheet mapping
- **WHEN** a Telegram user message arrives for a user whose Telegram `user_id` exists in the application mapping
- **THEN** `TelegramAdapterService` SHALL return the referenced spreadsheet id to initialize the correct FinanceAgent context

#### Scenario: Telegram user has no spreadsheet mapping
- **WHEN** a Telegram user id is not present in the user-to-spreadsheet mapping
- **THEN** `TelegramAdapterService` SHALL return an empty lookup result or safe failure signal rather than starting the FinanceAgent with an unrelated spreadsheet id

### Requirement: Telegram user id to spreadsheet id mapping is represented as a dictionary
The system SHALL provide a dictionary structure that maps a Telegram user id to the spreadsheet id of that user’s account.

#### Scenario: mapping is created in memory
- **WHEN** the adapter service is initialized in the application context
- **THEN** the system SHALL expose a mapping object with Telegram account keys and spreadsheet id values for selection by the service
