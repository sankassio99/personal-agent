## Context

The current Telegram integration in the application handler sends all normal user messages through the shared `FinanceAgent` adapter. The base agent infrastructure factory currently creates a `GoogleSheetsTools` object with a single hard-coded default range, `SAMPLE_RANGE_NAME = "'Despesas'!B1:E"`, and the `_create_agent` helper cannot accept a handler-provided range override. The new requirement requires a /summary flow that can switch the active spreadsheet region to the requested `'Sumário'!B27:F42` range.

## Goals / Non-Goals

**Goals:**
- Enable the Telegram handler to identify the `/summary` keyword and bind it to a summary behavior.
- Allow the handler to configure the range that the base agent’s Google Sheets tool should inspect.
- Preserve backward compatibility for the default summary/fallback range when no override is passed.

**Non-Goals:**
- Rewriting the `FinanceAgent` response generation semantics.
- Changing the repository’s existing GoogleSheetsTools dependency or authentication model.
- Introducing a brand-new command parser for all Telegram commands.

## Decisions

1. The handler will normalize incoming Telegram text before dispatch, treating `/summary` as a command indicator and then passing a keyword-specific `spreadsheet_range` value into the agent factory. This is the shortest and most testable seam because the handler already resolves the spreadsheet ID and assembles the instructions.

   Rationale: The Telegram handler is the only layer that has explicit knowledge of the user’s request and can choose a different worksheet view without changing the response agent’s public API.

2. The common agent builder in `BaseAgent._create_agent` will accept an optional `spreadsheet_range` keyword argument and feed it into `GoogleSheetsTools(spreadsheet_range=<range>)` only when provided. Otherwise it will continue to use the module-level default range constant.

   Rationale: This preserves the existing behavior while enabling the requested handler override with a minimal API expansion.

3. The range will be expressed consistently as the worksheet range string `"'Sumário'!B27:F42"` and treated as a handler-provided override object rather than a hard-coded constant in a utility. This supports future reuse for other commands and sheet windows.

   Rationale: The explicit range text keeps the spec and design document consistent with the user requirement and avoids introducing new configuration sources.

## Risks / Trade-offs

- [Risk] The handler needs explicit normalization for `/summary` so unrelated text remains unchanged. → Mitigation: The branch should operate only when the Telegram message text begins with the keyword and should ignore capitalization or surrounding whitespace.
- [Risk] Range-aware behavior increases coupling between the handler and base agent factory. → Mitigation: Keep the override keyword as an optional argument in `_create_agent`, with the existing fallback in place.
- [Risk] A range-specific Google Sheets query may fail if the worksheet or target region is missing. → Mitigation: Continue to use the existing `GoogleSheetsTools` error-return flow and keep fallback behavior explicit in the factory.

## Migration Plan

1. Extend the base agent `_create_agent` method signature to accept an optional `spreadsheet_range` parameter and pass it to `GoogleSheetsTools`.
2. Update the Telegram handler flow to normalize `/summary` messages and call the factory with the requested summary range.
3. Re-run the existing agent lifecycle tests and ensure the default fallback range is still used when the argument is omitted.
4. If the command is not recognized, allow the normal message flow to continue unchanged.

## Open Questions

- Whether other `/report`, `/expense`, or `/chart` conversation patterns should later reuse the same range override pattern.
- Whether the default summary range should be factored into a separate named constant for more resilient configuration management.
