## Context

The finance assistant already contains a created `add_expense` tool under the agent infrastructure layer. The tool uses the Google Sheets `append` API with `insertDataOption="INSERT_ROWS"` and receives a row payload of `[date, amount, description, category]` for the configured `SHEET_NAME` and `SPREADSHEET_ID`. That means the implementation should rely on the tool’s append semantics and on the repository’s spreadsheet resolution path rather than trying to recalculate the destination line in the planning layer.

The design therefore uses the existing code artifact as the reference interface for the next requirement update. The change should ensure that the handler / adapter path resolves the spreadsheet identity and sheet context, and then forwards the operation to the `add_expense` tool.

## Goals / Non-Goals

**Goals:**
- Use the created `add_expense` tool as the canonical Google Sheets write path for expenses.
- Make sure the spreadsheet id and range configuration come from the application’s existing Telegram mapping and sheet naming strategy.
- Keep the write behavior aligned with the tool’s `append` behavior and make the row placement logic implicit to the Sheets API.

**Non-Goals:**
- Replacing the repository’s `GoogleSheetsTools` support with a separate manual row calculator.
- Building a new expense insertion API outside of the existing agent tool structure.
- Introducing a different row-writing behavior than what the `append` API already provides.

## Decisions

1. Treat the created `add_expense` tool as the authoritative implementation contract for expense writes.
   - Rationale: The code already exists and uses the sheet append semantics that the tool asks for. Reworking the plan around that artifact keeps the design consistent with the implementation surface already present in the workspace.

2. Resolve the spreadsheet id from the Telegram adapter or routing layer before the tool is called.
   - Rationale: The file header already points to `TelegramAdapterService.resolve_spreadsheet_id`, which is the right cross-cutting context source for per-user spreadsheet ownership.

3. Use the existing Google Sheets `append` call rather than a hard-coded automatic row target.
   - Rationale: `append` is the natural API for a tool that should “add the expense to the next available row” without requiring an explicit line number in the request.

4. Keep the sheet name and range semantics consistent with the implementation stub.
   - Rationale: The tool currently declares `SHEET_NAME = "Despesas"` and writes values into `A:D`. The planning artifacts should avoid inventing a parallel or competing range convention.

## Risks / Trade-offs

- [Risk] The tool currently has a placeholder `SPREADSHEET_ID` and needs a resolved mapping from the adapter path. → Mitigation: Plan the integration to depend on `TelegramAdapterService.resolve_spreadsheet_id` and configuration, not on embedded constants.
- [Risk] The tool’s API call is a simple append and may not protect ordering beyond the sheet API behavior. → Mitigation: Keep the contract limited to the append semantics already shown in the implementation stub.
- [Risk] If the sheet is not the `Despesas` tab, the tool will target the wrong range. → Mitigation: Keep the active sheet context explicit in the adapter or settings rather than changing the tool’s range name in planning artifacts.

## Migration Plan

1. Keep the `add_expense` tool as the source of truth for the write operation.
2. Resolve the correct spreadsheet id via the Telegram adapter service or similar registry before the tool is invoked.
3. Ensure the use of the configured `Despesas` sheet range remains consistent with the tool’s append contract.
4. Verify the implementation behavior only through the existing Google Sheets append semantics and not through a separate row-discovery mechanism.

## Open Questions

- Which downstream adapter or handler will become the canonical caller for the created `add_expense` tool?
- Should the finished implementation expose a reusable wrapper that hides the spreadsheet id and sheet initialization details inside the repository layer?
- Does the `add_expense` tool need a normalized error response when the spreadsheet id is still unresolved?
