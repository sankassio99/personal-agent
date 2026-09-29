# Vertical Slice Architecture Proposal

## Status

Proposed for analysis. This document does not change runtime behavior.

## Context

The Finance Assistant is organized primarily by technical layer:

- `adapters` contains Telegram and MCP entry points.
- `application` contains handlers and services.
- `infrastructure` contains agents, configuration, and Google Sheets access.
- `domain` contains domain-oriented packages.

This separation is useful for shared infrastructure, but a product capability
currently spans several folders. For example, recording an expense involves a
Telegram handler, an agent tool, user-to-spreadsheet resolution, Google Sheets
access, and a budget alert. Implementing or changing that capability requires
following the flow across layers.

## Decision

Adopt a vertical slice architecture incrementally. Group code by a user-facing
capability, while retaining shared technical implementations in shared
infrastructure packages.

A slice owns its use-case inputs and results, application workflow, feature
specific adapters, and tests. Shared configuration, transport clients, and
cross-feature abstractions remain outside individual slices.

Use ports-and-adapters boundaries within and around each slice. Business code
depends on generic capabilities such as `ExpenseLedger`, `UserRegistry`, and
`MessageGateway`, never on a provider such as Google Sheets, Firebase,
PostgreSQL, Telegram, or WhatsApp. Provider implementations live at the
application edge and are selected only by the composition root.

## Proposed Structure

```text
src/finance_assistant/
  bootstrap/
    application.py
  shared/
    config.py
    agent/
      finance_agent.py
      prompts.py
  adapters/
    messaging/
      telegram_gateway.py
      whatsapp_gateway.py
    persistence/
      google_sheets/
        expense_ledger.py
        income_ledger.py
        budget_repository.py
      firebase/
        expense_ledger.py
        income_ledger.py
        budget_repository.py
      postgresql/
        expense_ledger.py
        income_ledger.py
        budget_repository.py
    identity/
      configured_user_registry.py
  features/
    expenses/
      commands.py
      service.py
      ports.py
      agent_tools.py
    income/
      commands.py
      service.py
      ports.py
      agent_tools.py
    budget_alerts/
      service.py
      policies.py
      ports.py
    daily_summary/
      service.py
      formatter.py
      job.py
      scheduler.py
      ports.py
    onboarding/
      service.py
      ports.py
  delivery/
    telegram/
      handlers.py
    whatsapp/
      webhook.py
  main.py
tests/
  features/
    expenses/
    income/
    budget_alerts/
    daily_summary/
    onboarding/
```

The exact file names may evolve. The important boundaries are that a feature's
workflow and tests are colocated, and that vendor-specific code stays in
`adapters` or `delivery`, outside feature services.

## Dependency Rules

1. Telegram, WhatsApp, Agno, and MCP modules are input/output adapters. They
   translate incoming data and call an application service; they do not contain
   business workflow or construct their own dependencies.
2. Feature services depend on explicit interfaces defined with
   `typing.Protocol`, such as `ExpenseLedger`, `UserRegistry`, and
   `MessageGateway`. They must not import a provider SDK or provider-specific
   type.
3. Google Sheets, Firebase, PostgreSQL, Telegram, and WhatsApp implementations
   satisfy those interfaces and remain replaceable in tests.
4. `bootstrap/application.py` is the single composition root. It reads
   provider configuration, creates the selected concrete adapters, injects them
   into feature services, then registers delivery handlers and schedules jobs.
5. A shared module is justified only when it supports more than one slice.
   Do not create generic abstractions before a second use case needs them.

## Python Implementation Pattern

Use dataclasses for the use-case boundary and protocols for dependencies:

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RecordExpense:
    user_id: int
    date: str
    amount: float
    description: str
    category: str


class ExpenseLedger(Protocol):
    def append(self, account_id: str, expense: RecordExpense) -> None: ...


class UserRegistry(Protocol):
    def account_for(self, user_id: int) -> str | None: ...
```

The `RecordExpenseService` uses these contracts. A Telegram command handler and
an Agno tool both translate their input into `RecordExpense` and invoke the
same service, so recording an expense has one implementation regardless of
entry point. The Google-Sheets adapter can translate the provider-neutral
account identifier into its spreadsheet identifier internally.

Pydantic is optional. Use it only when external data validation or
serialization needs exceed small, explicit dataclasses and adapter validation.

## Replacing Providers

Provider replacement changes composition and adapter implementations, not the
feature workflows:

| Change | Replace | Unchanged |
| --- | --- | --- |
| Google Sheets to Firebase | The `ExpenseLedger`, `IncomeLedger`, and budget repository implementations selected in `bootstrap/application.py`. | Expense recording, budget evaluation, summaries, and their tests against ports. |
| Google Sheets to PostgreSQL | The same persistence adapters; introduce migrations and transaction handling within the PostgreSQL adapter. | Feature service APIs and delivery adapters. |
| Telegram to WhatsApp | The delivery adapter and provider webhook/polling configuration. | Commands/use cases, persistence adapters, and notification intent. |

The messaging port should express application intent, for example
`send_text(recipient: UserAddress, text: str)`, rather than Telegram concepts
such as `chat_id`, `Update`, parse modes, or command handlers. The delivery
adapter maps the generic intent to Telegram or WhatsApp APIs. Provider-only
features, such as audio download or HTML formatting, are handled at that
adapter boundary and converted into a normalized feature input.

## Initial Slice Boundaries

| Slice | Current responsibility |
| --- | --- |
| `expenses` | Record expenses and request any post-recording actions. |
| `budget_alerts` | Evaluate category budget usage and send qualifying alerts. |
| `daily_summary` | Read daily expenses, generate summaries, schedule, and send them. |
| `income` | Record and query income. |
| `onboarding` | Resolve registered users and present registration guidance. |

## Expense and Budget Alert Boundary

The expense workflow should not import and invoke the budget implementation
directly. Instead, the expense service emits an application-level
`ExpenseRecorded` event or calls an injected `ExpenseRecordedHandler`.

```text
Telegram or Agno adapter
  -> RecordExpenseService
  -> ExpenseRepository
  -> ExpenseRecorded
  -> BudgetAlertService
```

The first implementation may execute the handler synchronously in process.
That keeps existing behavior without introducing a queue, worker, or message
broker. Introduce asynchronous delivery only when retry, failure isolation, or
latency requirements justify it.

## Incremental Migration Plan

1. Define provider-neutral ports (`UserRegistry`, `ExpenseLedger`,
   `IncomeLedger`, `BudgetRepository`, and `MessageGateway`) in the owning
   feature packages. Create Google Sheets and Telegram implementations behind
   those ports, while keeping compatibility wrappers for existing imports.
2. Create `features/expenses` and move the recording workflow behind
   `RecordExpenseService`. Do not expose Google Sheets identifiers in its
   command or result types.
3. Move budget evaluation and notification into `features/budget_alerts`.
   Inject it into the expense slice through an event handler or notifier
   interface, preserving the existing best-effort notification behavior.
4. Extract `features/daily_summary`, separating its scheduled-job adapter from
   summary creation and message delivery.
5. Migrate income, recurring entries, summary commands, and onboarding one
   capability at a time.
6. Move dependency construction and delivery-adapter registration to
   `bootstrap/application.py`. Reduce `main.py` to startup orchestration.
7. Move each feature's unit and integration tests beside its slice. Delete old
   layer-based modules only after callers and tests have moved.

## Benefits

- Feature changes have a smaller, more discoverable change surface.
- Telegram and agent/MCP entry points share the same business implementation.
- Telegram and WhatsApp can coexist during a delivery-channel migration.
- Google Sheets, Firebase, and PostgreSQL are provider implementations, not
  architectural dependencies of the finance features.
- Unit tests replace Google Sheets, Telegram, and registry integrations through
  small protocol-based fakes.
- Feature ownership and review become clearer as the assistant gains
  capabilities.
- Shared infrastructure remains available without forcing every feature into a
  generic service layer.

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Large folder move creates regressions and merge conflicts. | Migrate one feature at a time and retain compatibility wrappers temporarily. |
| Feature packages duplicate shared behavior. | Extract only demonstrated, cross-feature mechanisms into `shared`. |
| Event handling adds unnecessary complexity. | Start with synchronous in-process handlers; add durable asynchronous delivery only for demonstrated operational needs. |
| Provider abstractions mirror a vendor API and prevent replacement. | Design ports in the language of the finance feature; keep provider identifiers and SDK types inside adapters. |
| A messaging provider has different capabilities from Telegram. | Model only common business intents in `MessageGateway`; add narrowly scoped optional capabilities at the delivery edge. |
| User registration data remains coupled to application code. | Define a `UserRegistry` interface and move its implementation to configuration or persistent storage without exposing identifiers in source or logs. |

## Acceptance Criteria

The migration is complete when:

1. Each feature can be located under `features/<feature-name>`.
2. Telegram, WhatsApp, and Agno/MCP adapters call a feature service rather than performing
   business workflow directly.
3. Feature services have no direct dependency on Telegram, WhatsApp, Google,
   Firebase, or PostgreSQL SDKs and identifiers.
4. Dependency construction occurs in one composition root.
5. Changing the selected persistence or messaging provider requires no feature
   service change.
6. The current expense, budget alert, daily summary, income, and onboarding
   behaviors remain covered by focused unit or integration tests.
7. Runtime behavior remains unchanged unless a separate approved change
   explicitly modifies it.
