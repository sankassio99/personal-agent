# Design

## Context

The assistant already uses dedicated expense and income tools with spreadsheet ranges and user-specific spreadsheet mappings. Category lists are maintained in each workbook's `Sumário` tab at fixed ranges: `B30:B42` for expenses and `B49:B53` for income.

## Goals / Non-Goals

**Goals:**
- Add one read-only category tool that selects the correct summary range from a required entry type.
- Give the expense and income agent workflows explicit rules for category omission.
- Preserve explicit category values supplied by users.

**Non-Goals:**
- Editing category lists from Telegram.
- Inferring categories for historical spreadsheet data.
- Validating or replacing explicitly supplied categories.

## Decisions

1. **Use one typed category tool rather than separate expense and income tools.**
   Rationale: both lists share authentication, user resolution, response formatting, and a fixed worksheet. A required entry type selects the correct range without duplicating access logic.

2. **Read only non-empty cells in their spreadsheet order.**
   Rationale: the workbook remains the source of truth while blank cells do not become invalid choices. Preserving order makes the tool result predictable and easy to inspect.

3. **Require category retrieval only for omitted categories.**
   Rationale: user input takes precedence. Restricting inference to incomplete entries avoids silently rewriting a category selected by the user.

4. **Do not add an entry when no category can be inferred.**
   Rationale: asking for clarification protects the category data model from unsupported values.

## Risks / Trade-offs

- [The summary tab or configured range is unavailable] → Surface the Google Sheets failure and do not attempt category inference or a write.
- [The model chooses a weak category match] → Require it to use only returned values and ask the user when none is applicable.
- [Spreadsheet category ranges change] → Keep the ranges as named constants with targeted unit tests so future workbook updates are localized.

## Migration Plan

1. Add the category retrieval tool and tests for both fixed ranges.
2. Register the tool with the finance agent and update expense and income instructions.
3. Deploy with the existing Google Sheets credentials and user mapping; no worksheet migration is required.
