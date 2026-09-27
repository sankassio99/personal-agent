from datetime import datetime, time

from finance_assistant.application.services.recurrence_rule import (
    DailyRecurrence,
    MonthlyRecurrence,
    WeeklyRecurrence,
)


def test_daily_recurrence_returns_today_when_trigger_time_not_yet_passed():
    rule = DailyRecurrence(time(20, 0))

    next_run = rule.next_run(datetime(2026, 9, 18, 19, 30))

    assert next_run == datetime(2026, 9, 18, 20, 0)


def test_daily_recurrence_returns_tomorrow_when_trigger_time_already_passed():
    rule = DailyRecurrence(time(20, 0))

    next_run = rule.next_run(datetime(2026, 9, 18, 20, 30))

    assert next_run == datetime(2026, 9, 19, 20, 0)


def test_weekly_recurrence_returns_later_this_week_when_target_weekday_ahead():
    # 2026-09-18 is a Friday (weekday=4); target Monday (weekday=0) is 3 days ahead.
    rule = WeeklyRecurrence(weekday=0, trigger_time=time(9, 0))

    next_run = rule.next_run(datetime(2026, 9, 18, 10, 0))

    assert next_run == datetime(2026, 9, 21, 9, 0)


def test_weekly_recurrence_rolls_over_when_target_weekday_already_passed_today():
    # Target is the same weekday as the reference date, but the trigger time already passed.
    rule = WeeklyRecurrence(weekday=4, trigger_time=time(9, 0))

    next_run = rule.next_run(datetime(2026, 9, 18, 10, 0))

    assert next_run == datetime(2026, 9, 25, 9, 0)


def test_monthly_recurrence_returns_this_month_when_day_not_yet_passed():
    rule = MonthlyRecurrence(day_of_month=15, trigger_time=time(9, 0))

    next_run = rule.next_run(datetime(2026, 9, 1, 0, 0))

    assert next_run == datetime(2026, 9, 15, 9, 0)


def test_monthly_recurrence_rolls_over_to_next_month_when_day_already_passed():
    rule = MonthlyRecurrence(day_of_month=15, trigger_time=time(9, 0))

    next_run = rule.next_run(datetime(2026, 9, 20, 0, 0))

    assert next_run == datetime(2026, 10, 15, 9, 0)


def test_monthly_recurrence_skips_months_without_the_configured_day():
    # Day 31 does not exist in February or April; next valid month is March.
    rule = MonthlyRecurrence(day_of_month=31, trigger_time=time(9, 0))

    next_run = rule.next_run(datetime(2026, 2, 1, 0, 0))

    assert next_run == datetime(2026, 3, 31, 9, 0)


def test_monthly_recurrence_clamped_day_does_not_repeat_in_short_months():
    rule = MonthlyRecurrence(day_of_month=31, trigger_time=time(9, 0))

    next_run = rule.next_run(datetime(2026, 4, 1, 0, 0))

    assert next_run == datetime(2026, 5, 31, 9, 0)
