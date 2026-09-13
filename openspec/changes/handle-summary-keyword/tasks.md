## 1. Handler keyword and range plumbing

- [x] 1.1 Add a Telegram normalization branch that detects the `/summary` keyword and forwards the requested summary range override to the agent factory.
- [x] 1.2 Ensure the handler can pass the range `"'Sumário'!B27:F42"` through the message flow without changing the normal reply contract.

## 2. Agent factory compatibility

- [x] 2.1 Extend `BaseAgent._create_agent` so it accepts an optional `spreadsheet_range` keyword argument and passes it to `GoogleSheetsTools`.
- [x] 2.2 Preserve the default fallback with the existing `SAMPLE_RANGE_NAME` value when the override is not supplied.

## 3. Verification

- [x] 3.1 Add or update a regression test verifying the summary keyword handler branch and the range override propagation.
- [x] 3.2 Confirm the generated OpenSpec artifact set remains consistent with the repo’s change requirements.
