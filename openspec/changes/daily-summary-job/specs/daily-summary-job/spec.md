## ADDED Requirements

### Requirement: Scheduled daily summary job triggers at 20:00
The system SHALL schedule a background task that runs every day at 20:00 and invokes the daily summary flow for the configured finance data source.

#### Scenario: Schedule fires at the configured time
- **WHEN** the scheduler reaches 20:00 in the application timezone
- **THEN** the system SHALL call the daily summary pipeline for the relevant spreadsheet context.

### Requirement: Spreadsheet repository exposes filtered read support
The system SHALL provide a Google Sheets repository method named `get_sheet(spreadsheet_id, sheet_name, filter)` that returns rows matching the supplied filter criteria.

#### Scenario: Repository query is requested
- **WHEN** the daily summary service needs to read the current spreadsheet
- **THEN** the repository SHALL return the rows matching the provided filter without exposing raw Google API details to the service layer.

### Requirement: Daily summary service filters by current date
The system SHALL provide a service that receives spreadsheet rows and returns only records from the current date.

#### Scenario: Today’s records are requested
- **WHEN** the daily summary service is invoked for the current date
- **THEN** it SHALL include only rows whose date matches the current day and exclude unrelated records.

### Requirement: Structured summary payload is returned
The system SHALL return daily summary entries as structured records containing `date`, `value`, `description`, and `category`.

#### Scenario: Summary is formatted for delivery
- **WHEN** the daily summary service computes the filtered result
- **THEN** each result item SHALL include the date, value, description, and category fields in a stable object structure.
