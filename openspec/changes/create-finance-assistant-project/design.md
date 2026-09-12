## Context

The requested change introduces a new Python project called a finance assistant. The repository currently has an OpenSpec planning home but no implementation structure for a finance assistant package. The design should establish a clean and extensible project layout that separates user-facing Telegram integration, agent behavior, application orchestration, domain models, MCP tooling, infrastructure integrations, and configuration.

## Goals / Non-Goals

**Goals:**
- Provide a clean source layout for a Python finance assistant package under `src/finance_assistant`.
- Separate responsibilities into Telegram, application, agent, domain, MCP, infrastructure, and configuration components.
- Give the project a consistent structure for future implementation and tests.
- Create the repository metadata and environment guidance files expected by a Python project.

**Non-Goals:**
- Implementing every handler, agent, or data model in the first pass.
- Defining a production-grade deployment pipeline or database model.
- Making irreversible decisions about specific payment providers, APIs, or Google Sheets schema.

## Decisions

The design uses a layered package structure that follows the requested directory map:

- `src/finance_assistant/telegram/` owns the bot bootstrap and Telegram request handling.
- `src/finance_assistant/application/` owns orchestration and use-case services.
- `src/finance_assistant/agent/` owns finance reasoning prompts and the finance agent entrypoint.
- `src/finance_assistant/domain/` owns finance entities, value objects, and rules.
- `src/finance_assistant/mcp/` exposes tools through an MCP server and tool modules for expenses and reporting.
- `src/finance_assistant/infrastructure/google_sheets/` isolates Google Sheets repository patterns and client access.
- `src/finance_assistant/config/` centralizes settings and environment values.

This split reduces coupling between the Telegram UI adapter, the financial reasoning layer, and external data systems. It also allows each package boundary to evolve independently while keeping the project understandable.

For implementation, the project should follow a modern Python packaging style using `pyproject.toml`, an editable source layout under `src/`, and tests organized under `tests/unit/` and `tests/integration/`.

## Risks / Trade-offs

- [Risk] A package-first skeleton may introduce directories before their concrete responsibilities are implemented. → Mitigation: keep the skeleton minimal and document explicit ownership per directory.
- [Risk] The project may grow faster than its architecture. → Mitigation: enforce the requested package boundaries and avoid placing domain code directly in the Telegram or MCP layer.
- [Risk] Google Sheets integration may be chosen before a data model exists. → Mitigation: keep repository interfaces abstract and define the Google Sheets client/repository modules as adapters.

## Migration Plan

This is a greenfield project structure. There is no rollback or migration path required for existing repository behavior. The implementation should introduce the package skeleton and metadata files without altering current source code outside the new structure.

## Open Questions

- Which exact Python dependency manager and version constraints should the project adopt?
- Should the Telegram bot use a specific framework such as `python-telegram-bot` or a lightweight webhook adapter?
- Which Google Sheets service account and repository abstraction should be used in the first iteration?
