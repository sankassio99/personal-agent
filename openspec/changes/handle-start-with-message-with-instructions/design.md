## Context

The repository already contains a Telegram bot adapter and a Telegram message handler that processes ordinary text messages in the application handler layer. The current `handle_start` function is a minimal placeholder that replies with a generic `Starting` message, and the message handler path continues to build the FinanceAgent with a spreadsheet-based instruction string for all known message traffic. This change introduces a clearer conversation start experience that welcomes the user and provides a path to register or recover the spreadsheet mapping.

## Goals / Non-Goals

**Goals:**
- Create a Telegram `/start` listener experience that replies with a short introductory instruction message.
- Tell the user how to contact the administrator and give the Telegram user id plus email needed to create the Google Sheets spreadsheet.
- Keep the design aligned with the existing application service and Telegram handler structure.

**Non-Goals:**
- Creating spreadsheet records automatically.
- Replacing the current FinanceAgent message route.
- Adding a persistent database-backed registry in this change.

## Decisions

1. Keep the start command as a lightweight instruction-only handler.
   - Rationale: The repository already uses a simple handler structure, and this change only needs to provide a friendly, deterministic user message at command entry.

2. Centralize the message text using a small helper in the handler file.
   - Rationale: This keeps the reply path consistent with the conversation architecture while avoiding direct string duplication in command and message branches.

3. Use a temporary, human-readable fallback path for users without spreadsheet registration.
   - Rationale: The project currently uses an in-memory Telegram adapter service and an early no-mapping return is a safe design for a clear first implementation.

## Risks / Trade-offs

- [Unregistered users need a manual admin contact] → Mitigation: include a single Telegram contact handle and an email request in the `/start` instruction text.
- [Mapping remains dictionary-backed and in-memory] → Mitigation: keep the first implementation simple and label it as an adapter boundary that can later become persistent.
- [User message can be too long for Telegram UX] → Mitigation: keep the start response concise and focused on the action the user must take.

## Migration Plan

1. Introduce the start-command instruction message helper in the Telegram handler module.
2. Wire the Telegram bot runner to attach a `/start` command handler to the same handler file.
3. Continue to use the adapter service for spreadsheet resolution in the message branch.

## Open Questions

- Should the start instruction route check the Telegram user id directly or simply print a generic contact message?
- Should the bot runner register a command filter for `/start` in the same module as the message handler?
