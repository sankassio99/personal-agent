## Context

The project already has separate Telegram, MCP, and Google Sheets infrastructure packages, but the MCP server is only a placeholder and Telegram handlers send every non-command message to the general response agent. The change crosses those boundaries and must preserve the existing bot behavior for unrelated messages.

## Goals / Non-Goals

**Goals:**

- Provide a configured Google Spreadsheet MCP server entry point backed by the existing Google Sheets infrastructure.
- Make `/finance` a deterministic Telegram routing boundary, including extraction of the remaining user request.
- Keep the MCP integration testable through injected clients or adapters rather than requiring live Google credentials in unit tests.
- Document required configuration and failure behavior.

**Non-Goals:**

- Define a complete personal-finance data model or add unrelated spreadsheet features.
- Change the behavior of ordinary conversational messages.
- Implement authentication, authorization, or multi-user spreadsheet isolation beyond the credentials/configuration already supported by the project.

## Decisions

- **Use a dedicated MCP routing/service boundary.** Telegram handlers will recognize the keyword and call a finance MCP service/tool adapter; they will not construct Google API requests directly. This keeps transport concerns separate from spreadsheet operations and leaves the generic response agent unchanged.
- **Treat `/finance` as a command-like prefix.** Matching will be case-insensitive, accept the keyword at the start of the trimmed message, and pass the remainder as the finance request. A bare keyword will produce an explicit usage/error response rather than invoking the general agent.
- **Reuse the existing Google Sheets client and repository abstractions.** Configuration will be supplied through the existing settings pattern and the MCP layer will depend on those abstractions, allowing fake clients in tests and avoiding duplicated credential logic.
- **Fail explicitly when MCP or Google Sheets configuration is unavailable.** Startup/configuration errors and request failures will be logged and returned as a clear user-facing error; they will not silently fall back to generic chat handling.
- **Register routing before the generic text handler.** Telegram command/prefix handling must claim `/finance` messages before the catch-all handler, while ordinary text continues to use `GeminiResponseAgent`.

## Risks / Trade-offs

- [Risk] Google credential or spreadsheet configuration is absent in deployment → Validate required settings at MCP initialization and provide actionable errors.
- [Risk] Prefix parsing could capture messages unintentionally → Match only a trimmed, leading `/finance` token with a valid boundary and cover near-miss cases in tests.
- [Risk] Live Google API behavior is difficult to test locally → Keep unit tests at the adapter boundary and make integration configuration explicit in documentation.
