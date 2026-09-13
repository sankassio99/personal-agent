## Why

The Telegram handler currently answers only normal conversation messages and never recognizes a summary-oriented keyword path. The finance assistant also constructs its default Google Sheets tool range inside the shared agent factory, so a summary command cannot intentionally point at a different sheet region such as the `Sumário` tab without a configurable range override.

## What Changes

- Add a Telegram command/keyword recognition path for the `/summary` input so the handler can choose a summary-specific response flow.
- Thread a `spreadsheet_range` argument through the base agent `_create_agent` factory so the Google Sheets tool receives a range configured by the handler rather than being fixed to the existing default.
- Standardize the summary range reference to the requested worksheet range `'Sumário'!B27:F42` and keep the default fallback unchanged when no range is explicitly passed.
- Keep the implementation isolated to the Telegram handler and the shared agent factory flow so the finance response adapter contract remains stable.

## Capabilities

### New Capabilities
- `telegram-summary-command`: Add a capability that recognizes the `/summary` keyword and routes the handler through the requested Google Sheets range configuration.

### Modified Capabilities
- `base-agent-factory`: Extend the reusable agent factory so it can accept an override `spreadsheet_range` value from the handler rather than forcing the default sample range in the constructor.

## Impact

- Affects the Telegram message entrypoint in the application handler layer.
- Affects the reusable base agent abstraction in the infrastructure agent factory.
- Creates a new request path that passes a handler-provided range to the Google Sheets tool adapter without breaking the existing finance agent response contract.
