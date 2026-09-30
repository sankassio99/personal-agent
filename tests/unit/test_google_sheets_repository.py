from finance_assistant.adapters.repositories.google_sheets_repository import GoogleSheetsRepository


class FakeSheetsService:
    def __init__(self, rows_by_spreadsheet):
        self.rows_by_spreadsheet = rows_by_spreadsheet
        self.requests = []

    def spreadsheets(self):
        service = self

        class Spreadsheets:
            def values(self):
                class Values:
                    def get(self, spreadsheetId, range):
                        service.requests.append((spreadsheetId, range))

                        class Request:
                            def execute(self):
                                return {"values": service.rows_by_spreadsheet.get(spreadsheetId, [])}

                        return Request()

                return Values()

        return Spreadsheets()


def test_get_category_budget_matches_category_and_returns_budget_columns(monkeypatch):
    sheets_service = FakeSheetsService(
        {"client-a": [["Food", "", "500", "425", "75"], ["Transport", "", "100", "40", "60"]]}
    )
    repository = GoogleSheetsRepository()
    monkeypatch.setattr(repository, "_build_service", lambda: sheets_service)

    result = repository.get_category_budget("client-a", "Transport")

    assert result == {"category": "Transport", "planned": "100", "actual": "40", "difference": "60"}
    assert sheets_service.requests == [("client-a", "'Sumário'!B27:F42")]


def test_get_category_budget_returns_none_when_category_is_missing(monkeypatch):
    sheets_service = FakeSheetsService({"client-a": [["Food", "", "500", "425", "75"]]})
    repository = GoogleSheetsRepository()
    monkeypatch.setattr(repository, "_build_service", lambda: sheets_service)

    assert repository.get_category_budget("client-a", "Transport") is None


def test_get_category_budget_uses_each_requested_client_spreadsheet(monkeypatch):
    sheets_service = FakeSheetsService(
        {
            "client-a": [["Food", "", "500", "425", "75"]],
            "client-b": [["Food", "", "200", "100", "100"]],
        }
    )
    repository = GoogleSheetsRepository()
    monkeypatch.setattr(repository, "_build_service", lambda: sheets_service)

    client_a_budget = repository.get_category_budget("client-a", "Food")
    client_b_budget = repository.get_category_budget("client-b", "Food")

    assert client_a_budget["planned"] == "500"
    assert client_b_budget["planned"] == "200"
    assert sheets_service.requests == [
        ("client-a", "'Sumário'!B27:F42"),
        ("client-b", "'Sumário'!B27:F42"),
    ]