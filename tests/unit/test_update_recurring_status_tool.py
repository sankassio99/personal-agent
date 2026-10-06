from types import SimpleNamespace

import pytest

from finance_assistant.adapters.agents.tools.update_recurring_status_tool import (
    update_recurring_status,
)


def configure_sheets(monkeypatch, rows, updates):
    class Request:
        def __init__(self, result):
            self.result = result

        def execute(self):
            return self.result

    class Values:
        def get(self, **kwargs):
            return Request({"values": rows})

        def update(self, **kwargs):
            updates.append(kwargs)
            return Request({"updatedRange": kwargs["range"]})

    class Sheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: Values())

    monkeypatch.setattr(
        "finance_assistant.adapters.agents.tools.update_recurring_status_tool._get_sheets_service",
        lambda: Sheets(),
    )


@pytest.mark.parametrize(
    ("requested_status", "expected_status"),
    [("paga", "Pago"), ("PENDENTE", "Pendente")],
)
def test_update_recurring_status_normalizes_status_and_updates_column_e(
    monkeypatch, requested_status, expected_status
):
    updates = []
    configure_sheets(monkeypatch, [["Name", "Amount"], [" Digi   Internet ", "30"]], updates)

    result = update_recurring_status.entrypoint(
        recurring_name="digi internet",
        status=requested_status,
        spreadsheet_id="sheet-id",
    )

    assert expected_status in result
    assert updates == [
        {
            "spreadsheetId": "sheet-id",
            "range": "Recorrentes!E2",
            "valueInputOption": "USER_ENTERED",
            "body": {"values": [[expected_status]]},
        }
    ]


@pytest.mark.parametrize(
    ("rows", "expected_message"),
    [
        (
            [["Name"], ["Vodafone"], [], ["Meo"]],
            "Available recurring payments: Vodafone, Meo.",
        ),
        ([["Name"], ["Digi Internet"], ["digi  internet"]], "More than one"),
    ],
)
def test_update_recurring_status_does_not_write_for_missing_or_ambiguous_names(
    monkeypatch, rows, expected_message
):
    updates = []
    configure_sheets(monkeypatch, rows, updates)

    result = update_recurring_status.entrypoint(
        recurring_name="digi internet",
        status="pago",
        spreadsheet_id="sheet-id",
    )

    assert expected_message in result
    assert updates == []


def test_update_recurring_status_rejects_invalid_status_without_sheets_request(monkeypatch):
    monkeypatch.setattr(
        "finance_assistant.adapters.agents.tools.update_recurring_status_tool._get_sheets_service",
        lambda: pytest.fail("Google Sheets must not be accessed for an invalid status."),
    )

    with pytest.raises(ValueError, match="Pago or Pendente"):
        update_recurring_status.entrypoint(
            recurring_name="digi internet",
            status="cancelado",
            spreadsheet_id="sheet-id",
        )


@pytest.mark.parametrize(("operation", "error", "expected_message"), [
    ("get", RuntimeError("read failed"), "Unable to read recurring payments"),
    ("update", RuntimeError("write failed"), "Unable to update recurring payment status"),
])
def test_update_recurring_status_surfaces_google_sheets_failures(
    monkeypatch, operation, error, expected_message
):
    class Values:
        def get(self, **kwargs):
            if operation == "get":
                raise error
            return SimpleNamespace(execute=lambda: {"values": [["Name"], ["Digi Internet"]]})

        def update(self, **kwargs):
            raise error

    class Sheets:
        def spreadsheets(self):
            return SimpleNamespace(values=lambda: Values())

    monkeypatch.setattr(
        "finance_assistant.adapters.agents.tools.update_recurring_status_tool._get_sheets_service",
        lambda: Sheets(),
    )

    with pytest.raises(RuntimeError, match=expected_message):
        update_recurring_status.entrypoint(
            recurring_name="digi internet",
            status="pago",
            spreadsheet_id="sheet-id",
        )
