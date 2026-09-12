## ADDED Requirements

### Requirement: finance assistant project structure
The system SHALL provide a Python project skeleton organized around a `src/finance_assistant` package containing Telegram integration, application services, finance agent logic, domain entities and value objects, MCP server tooling, Google Sheets infrastructure adapters, and configuration.

#### Scenario: requested project layout
- **WHEN** a developer opens the repository
- **THEN** the project SHALL expose a clear package hierarchy matching the requested finance assistant structure

### Requirement: project metadata and test scaffolding
The system SHALL include repository metadata and test directory scaffolding such as `pyproject.toml`, `.env.example`, `.gitignore`, `README.md`, and test folders for unit and integration coverage.

#### Scenario: package metadata is present
- **WHEN** a developer prepares the repository for implementation
- **THEN** the repository SHALL include the requested Python metadata and environment/example files and a tests structure
