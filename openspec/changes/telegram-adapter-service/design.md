## Context

The repository already contains a Telegram bot runner in the application adapter layer and a Telegram message handler that constructs a `FinanceAgent` with a static instruction string containing a single Google Sheet sample identifier. This is acceptable for demonstration purposes, but it cannot scale to a shared bot environment where the conversation sender should be connected to the correct spreadsheet id for that user’s finance workspace.

## Goals / Non-Goals

**Goals:**
- Add a `TelegramAdapterService` application service that resolves a Telegram user id into a spreadsheet id.
- Introduce a dictionary-based registry for the Telegram-user-to-spreadsheet relationship.
- Preserve an existing application flow that starts the FinanceAgent only after the correct user-specific spreadsheet id has been identified.

**Non-Goals:**
- Replacing the Telegram bot framework or the `FinanceAgent` conversation abstraction.
- Implementing a full database-backed identity model or OAuth flow.
- Automatically creating spreadsheets for new users.

## Decisions

1. Represent the source of truth for user-to-spreadsheet routing as a dictionary keyed by Telegram user id.
   - Rationale: The repo already uses lightweight Python settings objects and direct environment-backed configuration patterns, so an in-memory dictionary is a minimal, understandable first implementation.

2. Create a dedicated `TelegramAdapterService` in the application service layer.
   - Rationale: A service object isolates Telegram message context handling from the handler itself and creates a single place where user resolution, spreadsheet id lookup, and agent bootstrap context can be orchestrated.

3. Resolve the spreadsheet id before the agent response is constructed.
   - Rationale: The current handler builds an `instructions` string with a constant spreadsheet id in the same place as the message response. The new service should determine the correct spreadsheet id before the agent is initialized or instructed.

4. Keep the mapping implementation intentionally simple and replaceable.
   - Rationale: A dictionary can later evolve into a repository-backed mapping; this preserves a clear boundary while preventing speculation about storage mechanisms.

## Risks / Trade-offs

- [In-memory map is not durable] → Mitigation: treat the dictionary as a first adapter implementation and move the mapping to a persistent repository in a later change.
- [Telegram user ids can vary by chat context] → Mitigation: normalize and validate the user id source in the service before dictionary lookup.
- [Unknown user fallback is ambiguous] → Mitigation: return a safe fallback message or raise a clear service exception when no spreadsheet mapping exists.

## Migration Plan

1. Add `TelegramAdapterService` under the finance assistant application service layer.
2. Add the user-to-spreadsheet dictionary structure and seed it from the configured environment or default settings objects.
3. Replace the handler’s static sample spreadsheet id construction with a call to the adapter service.
4. Verify that the service returns the user’s spreadsheet id and lets the FinanceAgent begin with the correct account context.

## Open Questions

- Should the mapping dictionary be seeded from a `settings` object, an environment variable, or a repository-backed registry?
- Should the adapter support a `None` or `UnknownUser` fallback that sends a reply asking the user to register a spreadsheet id?
