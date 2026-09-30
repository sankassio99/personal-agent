import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from finance_assistant.adapters.telegram import telegram_service
from finance_assistant.features.budget_notification import service as budget_notification_service
from finance_assistant.infrastructure.agents import add_expense_tool


def configure_expense_workflow(monkeypatch, actual, failure=None):
    events = []
    messages = []

    class AppendRequest:
        def execute(self):
            events.append("write")
            if failure == "write":
                raise RuntimeError("expense write failed")
            return {"updates": {"updatedRange": "Despesas!A4"}}

    class Values:
        def append(self, **kwargs):
            return AppendRequest()

    class Sheets:
        def spreadsheets(self):
            class Spreadsheet:
                def values(self):
                    return Values()

            return Spreadsheet()

    class BudgetRepository:
        def get_category_budget(self, spreadsheet_id, category):
            events.append("lookup")
            assert spreadsheet_id == "client-spreadsheet"
            assert category == "Food"
            if failure == "lookup":
                raise RuntimeError("budget lookup failed")
            return {"category": category, "planned": "100", "actual": str(actual), "difference": "0"}

    class TelegramAdapter:
        def resolve_spreadsheet_id(self, telegram_user_id):
            assert telegram_user_id == "client-1"
            return "client-spreadsheet"

    class TelegramService:
        def send_message(self, chat_id, text):
            events.append("notification")
            messages.append((chat_id, text))
            if failure == "delivery":
                raise RuntimeError("telegram delivery failed")

    monkeypatch.setattr(add_expense_tool, "_get_sheets_service", lambda: Sheets())
    monkeypatch.setattr(budget_notification_service, "GoogleSheetsRepository", BudgetRepository)
    monkeypatch.setattr(budget_notification_service, "TelegramAdapterService", TelegramAdapter)
    monkeypatch.setattr(telegram_service, "TelegramService", TelegramService)

    return events, messages


@pytest.mark.parametrize(
    ("actual", "expected_message"),
    [
        ("70", None),
        ("70.01", "quase atingido"),
        ("100", "quase atingido"),
        ("100.01", "ultrapassado"),
    ],
)
def test_expense_workflow_sends_only_the_qualifying_separate_alert(monkeypatch, actual, expected_message):
    events, messages = configure_expense_workflow(monkeypatch, actual)

    result = add_expense_tool.add_expense.entrypoint(
        date="2026-09-14",
        amount=10.25,
        description="groceries",
        category="Food",
        spreadsheet_id="client-spreadsheet",
        telegram_user_id="client-1",
    )

    assert result == "Expense added successfully. Range: Despesas!A4"
    assert events[:2] == ["write", "lookup"]
    if expected_message is None:
        assert messages == []
    else:
        assert events == ["write", "lookup", "notification"]
        assert len(messages) == 1
        chat_id, message = messages[0]
        assert chat_id == "client-1"
        assert expected_message in message
        assert "Food" in message
        assert "€" in message


def test_failed_expense_write_does_not_look_up_or_notify_budget(monkeypatch):
    events, messages = configure_expense_workflow(monkeypatch, "95", failure="write")

    with pytest.raises(RuntimeError, match="Unable to append the expense row"):
        add_expense_tool.add_expense.entrypoint(
            date="2026-09-14",
            amount=10.25,
            description="groceries",
            category="Food",
            spreadsheet_id="client-spreadsheet",
            telegram_user_id="client-1",
        )

    assert events == ["write"]
    assert messages == []


def test_telegram_handler_passes_user_context_to_expense_notification(monkeypatch):
    from finance_assistant.adapters.telegram.telegram_adapter_service import TelegramAdapterService
    from finance_assistant.features.message.handler import handle_message

    events, messages = configure_expense_workflow(monkeypatch, "95")
    telegram_adapter_service = TelegramAdapterService()
    monkeypatch.setattr(telegram_adapter_service, "resolve_spreadsheet_id", lambda telegram_user_id: "client-spreadsheet")

    class DummyFinanceAgent:
        def __init__(self, **kwargs):
            pass

        def respond(self, message):
            return add_expense_tool.add_expense.entrypoint(
                date="2026-09-14",
                amount=10.25,
                description="groceries",
                category="Food",
                spreadsheet_id="client-spreadsheet",
            )

    monkeypatch.setattr(
        "finance_assistant.features.message.handler.TelegramAdapterService",
        lambda: telegram_adapter_service,
    )
    monkeypatch.setattr(
        "finance_assistant.features.message.handler.FinanceAgent",
        DummyFinanceAgent,
    )
    reply_text = AsyncMock()
    user = SimpleNamespace(id="client-1")
    update = SimpleNamespace(
        effective_user=user,
        message=SimpleNamespace(from_user=user, reply_text=reply_text),
    )

    update.message.text = "add groceries"
    asyncio.run(handle_message(update, None))

    assert events == ["write", "lookup", "notification"]
    assert messages[0][0] == "client-1"
    reply_text.assert_awaited_once()


@pytest.mark.parametrize("failure", ["lookup", "delivery"])
def test_notification_failure_does_not_change_successful_expense_result(monkeypatch, caplog, failure):
    events, _ = configure_expense_workflow(monkeypatch, "95", failure=failure)

    result = add_expense_tool.add_expense.entrypoint(
        date="2026-09-14",
        amount=10.25,
        description="groceries",
        category="Food",
        spreadsheet_id="client-spreadsheet",
        telegram_user_id="client-1",
    )

    assert result == "Expense added successfully. Range: Despesas!A4"
    assert "Budget notification failed after expense was recorded" in caplog.text
    assert events[0] == "write"