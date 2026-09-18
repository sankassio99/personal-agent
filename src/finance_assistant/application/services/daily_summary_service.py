"""Daily summary service for filtering finance rows by the current date."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)


class DailySummaryService:
    """Return a structured daily summary payload from sheet rows."""

    def filter_by_current_date(self, rows: list[list[Any]], today: date | None = None) -> list[dict[str, Any]]:
        """Return rows matching the current day as normalized summary objects."""
        current_day = today or date.today()
        filtered: list[dict[str, Any]] = []

        for row in rows:
            if len(row) < 4:
                continue

            row_date = str(row[0]).strip()
            if row_date != current_day.isoformat():
                continue

            value = row[1]
            description = row[2]
            category = row[3]

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                logger.warning("Ignoring row with non-numeric value for summary: %s", row)
                continue

            filtered.append(
                {
                    "date": row_date,
                    "value": numeric_value,
                    "description": str(description),
                    "category": str(category),
                }
            )

        return filtered
