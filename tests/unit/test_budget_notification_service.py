import logging

import pytest

from finance_assistant.application.services.budget_notification_service import BudgetNotificationService


class FakeRepository:
    def __init__(self, budget):
        self.budget = budget
        self.requests = []

    def get_category_budget(self, spreadsheet_id, category):
        self.requests.append((spreadsheet_id, category))
        return self.budget


class FakeTelegramAdapter:
    def resolve_spreadsheet_id(self, telegram_user_id):
        return "spreadsheet-for-client" if telegram_user_id == "client" else None


class FakeTelegramService:
    def __init__(self):
        self.messages = []

    def send_message(self, chat_id, text):
        self.messages.append((chat_id, text))


def create_service(budget):
    repository = FakeRepository(budget)
    telegram_service = FakeTelegramService()
    service = BudgetNotificationService(
        repository=repository,
        telegram_service=telegram_service,
        telegram_adapter=FakeTelegramAdapter(),
    )
    return service, repository, telegram_service


@pytest.mark.parametrize(
    ("actual", "expected_message"),
    [
        ("70", None),
        ("70.01", "quase atingido"),
        ("100", "quase atingido"),
        ("100.01", "ultrapassado"),
    ],
)
def test_budget_notification_thresholds_and_alert_precedence(actual, expected_message):
    service, repository, telegram_service = create_service(
        {"category": "Food", "planned": "100", "actual": actual, "difference": "0"}
    )

    sent = service.notify_if_needed("client", "Food")

    assert sent is (expected_message is not None)
    assert repository.requests == [("spreadsheet-for-client", "Food")]
    if expected_message is None:
        assert telegram_service.messages == []
    else:
        assert len(telegram_service.messages) == 1
        chat_id, message = telegram_service.messages[0]
        assert chat_id == "client"
        assert expected_message in message
        assert "Food" in message
        assert "€" in message


@pytest.mark.parametrize(
    "budget",
    [
        None,
        {"category": "Food", "planned": "0", "actual": "20"},
        {"category": "Food", "planned": "invalid", "actual": "80"},
        {"category": "Food", "planned": "100", "actual": "invalid"},
    ],
)
def test_invalid_or_non_positive_budget_does_not_send_notification(budget):
    service, _, telegram_service = create_service(budget)

    assert service.notify_if_needed("client", "Food") is False
    assert telegram_service.messages == []


def test_unmapped_client_does_not_read_budget_or_send_notification():
    service, repository, telegram_service = create_service(
        {"category": "Food", "planned": "100", "actual": "90"}
    )

    assert service.notify_if_needed("unknown", "Food") is False
    assert repository.requests == []
    assert telegram_service.messages == []


def test_budget_notification_logs_processing_stages_without_client_details(caplog):
    service, _, _ = create_service(
        {"category": "Food", "planned": "100", "actual": "90"}
    )

    with caplog.at_level(logging.DEBUG):
        assert service.notify_if_needed("client", "Food") is True

    assert "Budget notification processing started." in caplog.text
    assert "Spreadsheet resolved; looking up category budget data." in caplog.text
    assert "Category budget data retrieved" in caplog.text
    assert "Budget alert selected: near_limit." in caplog.text
    assert "Budget notification sent successfully." in caplog.text
    assert "spreadsheet-for-client" not in caplog.text
    assert "client" not in caplog.text