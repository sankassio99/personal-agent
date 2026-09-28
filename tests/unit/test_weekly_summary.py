from datetime import date, datetime, time

from finance_assistant.application.services.weekly_summary_message_formatter import (
    DEFAULT_CATEGORY_EMOJI,
    WeeklySummaryMessageFormatter,
)
from finance_assistant.application.services.weekly_summary_scheduler import WeeklySummaryScheduler
from finance_assistant.application.services.weekly_summary_service import WeeklySummaryService


def test_weekly_summary_filters_completed_week_boundaries_and_supported_dates():
    service = WeeklySummaryService()

    summary = service.summarize(
        [
            ["2026-09-20", "€10.00", "Start", "Supermercado"],
            ["", "26/09/2026", "€20,50", "End", "Transporte"],
            ["2026-09-19", "€30.00", "Before", "Extras"],
            ["2026-09-27", "€40.00", "After", "Extras"],
            ["invalid-date", "€50.00", "Invalid", "Extras"],
            ["2026-09-21", "invalid", "Invalid", "Extras"],
        ],
        reference_date=date(2026, 9, 27),
    )

    assert summary == {
        "start_date": date(2026, 9, 20),
        "end_date": date(2026, 9, 26),
        "categories": [
            {"category": "Supermercado", "total": 10.0},
            {"category": "Transporte", "total": 20.5},
        ],
        "grand_total": 30.5,
    }


def test_weekly_summary_aggregates_categories_and_grand_total():
    service = WeeklySummaryService()

    summary = service.summarize(
        [
            ["2026-09-20", "10.00", "Market", "Supermercado"],
            ["2026-09-21", "5.25", "Market", "Supermercado"],
            ["2026-09-22", "20.00", "Taxi", "Transporte"],
        ],
        reference_date=date(2026, 9, 27),
    )

    assert summary["categories"] == [
        {"category": "Supermercado", "total": 15.25},
        {"category": "Transporte", "total": 20.0},
    ]
    assert summary["grand_total"] == 35.25


def test_weekly_summary_formatter_formats_categories_and_uses_fallback_emoji():
    formatter = WeeklySummaryMessageFormatter()

    message = formatter.format(
        {
            "start_date": date(2026, 9, 20),
            "end_date": date(2026, 9, 26),
            "categories": [
                {"category": " supermercado ", "total": 49.52},
                {"category": "Unmapped", "total": 2.0},
            ],
            "grand_total": 51.52,
        }
    )

    assert message == (
        "📊 <b>Resumo de gastos da semana (20/09/2026 a 26/09/2026)</b>:\n\n"
        "• 🛒  supermercado : €49.52\n"
        f"• {DEFAULT_CATEGORY_EMOJI} Unmapped: €2.00\n\n"
        "• 💰 <b>Total da semana</b>: €51.52"
    )


def test_weekly_summary_formatter_has_empty_state():
    formatter = WeeklySummaryMessageFormatter()

    message = formatter.format(
        {
            "start_date": date(2026, 9, 20),
            "end_date": date(2026, 9, 26),
            "categories": [],
            "grand_total": 0.0,
        }
    )

    assert message == (
        "📊 <b>Resumo de gastos da semana (20/09/2026 a 26/09/2026)</b>:\n\n"
        "Nenhum gasto registrado nesta semana."
    )


def test_weekly_summary_scheduler_targets_sunday_at_9pm():
    scheduler = WeeklySummaryScheduler(trigger_time=time(21, 0))

    delay = scheduler._compute_seconds_until_next_run(datetime(2026, 9, 21, 20, 30))

    assert delay == 6 * 24 * 60 * 60 + 30 * 60
