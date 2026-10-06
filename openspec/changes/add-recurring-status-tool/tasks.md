# Tasks

## 1. Recurring status update tool

- [x] 1.1 Implement a dedicated recurring-status tool that resolves the active spreadsheet, reads the recurring rows, normalizes supported status requests, and updates only the matched row's column E; verify unit tests cover canonical `Pago` and `Pendente` writes.
- [x] 1.2 Implement unique normalized name matching that preserves sheet row positions while ignoring blank rows; verify unit tests cover case/whitespace-insensitive matches, missing names, and ambiguous names with no write request.
- [x] 1.3 Surface contextual failures for invalid statuses and Google Sheets read/write errors; verify unit tests assert the failure messages and absence of writes for invalid input.
- [x] 1.4 Return the non-empty recurring names from column A when no normalized match is found, without issuing a write; verify a unit test asserts the returned options and absence of update requests.

## 2. Agent integration

- [x] 2.1 Register the recurring-status tool in the recurring agent's tool composition without exposing it to unrelated command flows; verify the agent construction test includes the new tool.
- [x] 2.2 Update recurring-agent instructions so natural-language status requests invoke the dedicated tool and report its outcome; verify the instruction test or focused agent test covers `/recorrente atualiza o status da digi internet para paga`.

## 3. Integration validation

- [x] 3.1 Run the focused recurring-tool and agent tests with `.venv/bin/python3 -m pytest -q <selected tests>` and verify all pass.
- [x] 3.2 Run `openspec validate add-recurring-status-tool --strict` and verify the change artifacts satisfy the OpenSpec schema.
- [x] 3.3 Re-run the focused recurring-tool and agent tests after adding the unavailable-name options; verify all pass.
