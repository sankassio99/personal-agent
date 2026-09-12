## ADDED Requirements

### Requirement: Base agent factory
The system SHALL provide a reusable base agent class that creates an Agno `Agent` using a configured Gemini model provider and common agent settings.

#### Scenario: Create a structured response agent
- **WHEN** a developer instantiates the base agent abstraction
- **THEN** the class SHALL create an Agno `Agent` that accepts model, instructions, and message-oriented configuration without coupling the model directly to the Telegram handler

### Requirement: Gemini Lite model selection
The system SHALL allow the model identity to be configured as a Gemini 2.5 Flash Lite provider path consistent with the Agno integration style used in the JARVIS reference base agent.

#### Scenario: Select the Gemini Flash Lite model
- **WHEN** the project config resolves the provider model identifier
- **THEN** the agent factory SHALL construct a `Gemini` object with the expected model ID and API key configuration

### Requirement: Message response adapter
The system SHALL expose a message response workflow that accepts user input and returns a generated text message through a model-backed agent adapter.

#### Scenario: Produce a reply from a message
- **WHEN** a message is sent through the new response adapter
- **THEN** the adapter SHALL return a string response content that can be passed to the existing Telegram or MCP transport layer
