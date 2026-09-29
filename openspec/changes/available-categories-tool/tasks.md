# Tasks

## 1. Category retrieval tool

- [x] 1.1 Add a read-only category tool with an entry-type input that reads non-empty expense values from `Sumário!B30:B42` and income values from `Sumário!B49:B53`; verify unit tests assert both requested ranges and returned values.
- [x] 1.2 Resolve the requesting user's spreadsheet through the existing Telegram mapping and reject unmapped users without a Sheets request; verify unit tests cover mapped and unmapped cases.
- [x] 1.3 Reuse the existing Google Sheets service builder and preserve explicit read failures; verify a unit test asserts the propagated failure.

## 2. Agent category inference

- [x] 2.1 Register the category tool with the finance agent; verify the agent construction test includes the tool.
- [x] 2.2 Add expense instructions that require retrieving available expense categories before inferring an omitted category, preserve explicit categories, and ask for clarification when no match exists; verify instruction-content tests cover all outcomes.
- [x] 2.3 Add equivalent income instructions that use the income category list only when the income category is omitted; verify instruction-content tests cover the income workflow.

## 3. Integration validation

- [x] 3.1 Run the focused category tool and agent instruction tests with `python3 -m pytest`; verify they pass.
- [x] 3.2 Validate the completed OpenSpec change with `openspec validate available-categories-tool --strict`; verify the command succeeds.
