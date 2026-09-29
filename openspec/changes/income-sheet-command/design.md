# Design

## Context

The assistant already maps Telegram users to spreadsheet IDs and exposes tools that operate on the `Despesas` tab. The income workflow must use the same identity isolation and Google Sheets credential path while operating on `Rendimentos!B:E`.

## Goals / Non-Goals

**Goals:**
- Add income-specific read and append tools that follow the established expense-tool behavior.
- Route `/rendimentos` to an agent configuration whose spreadsheet range is `Rendimentos!B:E`.
- Make `/ajuda` disclose the new command.

**Non-Goals:**
- Changing expense worksheet behavior or its commands.
- Creating new spreadsheets or tabs.
- Defining income analytics, recurring income, or monthly totals.

## Decisions

1. **Use dedicated income tools with the existing Sheets service builder.**
   Rationale: the income tab has a distinct column range and user-facing intent, while the established service builder preserves the configured authentication and error handling. Reusing expense tools with conditionals would make tool descriptions and agent selection ambiguous.

2. **Reuse the existing Telegram-user-to-spreadsheet mapping.**
   Rationale: income and expenses belong to the same user's workbook, so a second mapping would duplicate configuration and risk cross-user access.

3. **Configure the `/rendimentos` agent with a fixed `Rendimentos!B:E` range.**
   Rationale: explicit range selection prevents generic sheet tools from reading or writing the expense tab during income interactions.

4. **Append values rather than targeting row numbers.**
   Rationale: appending to the next available row preserves existing income records and mirrors the established expense-writing behavior.

## Risks / Trade-offs

- [The `Rendimentos` tab or its expected columns are absent] → Return an explicit user-facing storage/read failure and log the underlying Sheets error.
- [An income interaction is interpreted as an expense] → Give the income tools and `/rendimentos` agent instructions explicit tab and record semantics.
- [A user is not registered] → Resolve the mapping before accessing Sheets and return the established registration guidance.

## Migration Plan

1. Add the income read/write tools and tests using `Rendimentos!B:E`.
2. Add `/rendimentos` routing and update `/ajuda`.
3. Deploy with the existing service-account configuration; no data migration is required.
4. Roll back by removing the command and income tools; no existing worksheet data needs to be changed.
