## Context

The project already has separate Telegram, Google Sheets infrastructure packages, and an Agno-style agent boundary, but the Telegram handlers send every non-command message to the general response agent. The change crosses those boundaries and must preserve the existing bot behavior for unrelated messages while replacing the spreadsheet MCP placeholder with a direct Google Sheets tool adapter matching the Agno Google Sheets toolkit documentation.

## Goals / Non-Goals

**Goals:**

- Provide a configured direct Agno GoogleSheetsTools Google Sheets adapter backed by the existing Google Sheets infrastructure settings.
- Make `/finance` a deterministic Telegram routing boundary, including extraction of the remaining user request.
- Keep the Google Sheets tool integration testable through injected clients or adapters rather than requiring live Google credentials in unit tests.
- Document required configuration and failure behavior.

**Non-Goals:**

- Define a complete personal-finance data model or add unrelated spreadsheet features.
- Change the behavior of ordinary conversational messages.
- Implement authentication, authorization, or multi-user spreadsheet isolation beyond the credentials/configuration already supported by the project.

## Decisions

- **Use a direct Agno GoogleSheetsTools integration boundary.** Telegram handlers will recognize the `/finance` keyword and call a finance service adapter that directly invokes the Agno Google Sheets toolkit, rather than constructing Google API calls or routing through a separate Google Spreadsheet MCP server. This keeps the transport boundary explicit while leaving the response agent available for ordinary text.
- **Treat `/finance` as a command-like prefix.** Matching will be case-insensitive, accept the keyword at the start of the trimmed message, and pass the remainder as the finance request. A bare keyword will produce an explicit usage/error response rather than invoking the general agent.
- **Reuse the existing Google Sheets client and repository abstractions as a seam, while aligning to the Agno Google Sheets toolkit contract.** Configuration will be supplied through the existing settings pattern and the service boundary will map those settings into the `GoogleSheetsTools` constructor parameters described by the documentation, while keeping the repository and client abstractions available for test doubles and explicit dependency boundaries.
- **Fail explicitly when Google Sheets authentication or spreadsheet configuration is unavailable.** Startup/configuration errors and request failures will be logged and returned as a clear user-facing error; they will not silently fall back to generic chat handling.
- **Register routing before the generic text handler.** Telegram command/prefix handling must claim `/finance` messages before the catch-all handler, while ordinary text continues to use `GeminiResponseAgent`.

## Risks / Trade-offs

- [Risk] Google credential or spreadsheet configuration is absent in deployment → Validate required settings at adapter initialization and provide actionable errors.
- [Risk] Prefix parsing could capture messages unintentionally → Match only a trimmed, leading `/finance` token with a valid boundary and cover near-miss cases in tests.
- [Risk] Live Google API behavior is difficult to test locally → Keep unit tests at the adapter boundary and make integration configuration explicit in documentation.
