## ADDED Requirements

### Requirement: Route finance keyword messages directly to Google Spreadsheet MCP
The Telegram bot SHALL route a message whose trimmed text begins with the case-insensitive `/finance` keyword and a valid token boundary directly to the Google Spreadsheet MCP finance service, passing the text after the keyword as the request through the Agno GoogleSheetsTools-backed service boundary.

#### Scenario: Finance request is routed
- **WHEN** a user sends `/finance show my spending this month`
- **THEN** the bot sends `show my spending this month` to the Google Spreadsheet MCP service and replies with its result

#### Scenario: Keyword matching is case-insensitive
- **WHEN** a user sends `/FINANCE add a coffee expense`
- **THEN** the bot routes `add a coffee expense` to the Google Spreadsheet MCP service

#### Scenario: Bare keyword is rejected clearly
- **WHEN** a user sends `/finance` without a request payload
- **THEN** the bot replies with a usage or missing-request error and does not call the generic response agent

### Requirement: Preserve non-finance message handling
Messages that do not match the `/finance` prefix SHALL continue through the existing generic response agent, and MCP routing failures SHALL be surfaced to the user rather than silently falling back to that agent.

#### Scenario: Ordinary text uses the response agent
- **WHEN** a user sends ordinary text that does not begin with `/finance`
- **THEN** the bot invokes the existing response agent and replies with its response

#### Scenario: Finance service fails
- **WHEN** a `/finance` request cannot be handled by the Google Spreadsheet MCP service
- **THEN** the bot logs the error and replies with a clear failure message without invoking the generic response agent
