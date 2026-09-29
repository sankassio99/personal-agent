"""Weekly expense summary aggregation service."""

from __future__ import annotations

import logging
from collections import OrderedDict
from datetime import date, timedelta
from typing import Any

from finance_assistant.application.services.daily_summary_service import DailySummaryService

logger = logging.getLogger(__name__)


class WeeklySummaryService:
    """Aggregate expense rows for the completed Sunday-to-Saturday week."""

    def week_bounds(self, reference_date: date | None = None) -> tuple[date, date]:
        """Return the Sunday-through-Saturday week completed before ``reference_date``."""
        current_date = reference_date or date.today()
        days_since_sunday = (current_date.weekday() + 1) % 7
        end_date = current_date - timedelta(days=days_since_sunday + 1)
        start_date = end_date - timedelta(days=6)
        return start_date, end_date

    def summarize(self, rows: list[list[Any]], reference_date: date | None = None) -> dict[str, object]:
        """Return category totals and the date range for the completed week."""
        start_date, end_date = self.week_bounds(reference_date)
        category_totals: OrderedDict[str, float] = OrderedDict()

        for row in rows or []:
            parsed = DailySummaryService._parse_row(row)
            if parsed is None:
                logger.info("Skipping row with an unsupported shape or date: %s", row)
                continue

            normalized_date, value, _, category = parsed
            try:
                row_date = date.fromisoformat(normalized_date)
                numeric_value = DailySummaryService._parse_money(value)
            except (TypeError, ValueError):
                logger.warning("Skipping row with an unparseable date or value: %s", row)
                continue

            if not start_date <= row_date <= end_date:
                continue

            category_name = str(category).strip() or "Sem categoria"
            category_totals[category_name] = category_totals.get(category_name, 0.0) + numeric_value

        categories = [
            {"category": category, "total": total}
            for category, total in category_totals.items()
        ]
        grand_total = sum(item["total"] for item in categories)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "categories": categories,
            "grand_total": grand_total,
        }
