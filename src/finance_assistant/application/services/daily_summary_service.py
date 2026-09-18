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

        if not rows:
            logger.warning("Daily summary received no rows for date %s.", current_day.isoformat())
            return filtered

        logger.info("___________________________________________________________")
        logger.info("Rows count: %s", len(rows))
        logger.info("First row sample: %s", rows[0])
        logger.info("___________________________________________________________")

        for row in rows:
            if not row:
                logger.info("Skipping empty row while filtering daily summary.")
                continue

            logger.info("Processing summary row for current date %s: %s", current_day.isoformat(), row)
            parsed = self._parse_row(row)
            if parsed is None:
                logger.info("Skipping row because it did not match a supported date/value shape: %s", row)
                continue

            row_date, value, description, category = parsed
            logger.info("Normalized row to date=%s, value=%s, description=%s, category=%s", row_date, value, description, category)

            if row_date != current_day.isoformat():
                logger.info("Skipping row because row_date=%s does not match current_day=%s", row_date, current_day.isoformat())
                continue

            try:
                numeric_value = self._parse_money(value)
            except (TypeError, ValueError):
                logger.warning("Ignoring row with non-numeric value for summary: %s", row)
                continue

            logger.info("Accepted row for summary: date=%s, value=%s, description=%s, category=%s", row_date, numeric_value, description, category)
            filtered.append(
                {
                    "date": row_date,
                    "value": numeric_value,
                    "description": str(description),
                    "category": str(category),
                }
            )

        return filtered

    @staticmethod
    def _parse_row(row: list[Any]) -> tuple[str, Any, Any, Any] | None:
        """Accept both the legacy 4-column format and the spreadsheet's 5-column format."""
        if len(row) >= 5:
            date_value, value, description, category = row[1], row[2], row[3], row[4]
            normalized_date = DailySummaryService._normalize_date(date_value)
            if normalized_date is not None:
                logger.info("Parsed 5-column row with date=%s", normalized_date)
                return normalized_date, value, description, category
            logger.info("Could not normalize 5-column date value from row: %s", row)
            return None

        if len(row) >= 4:
            date_value, value, description, category = row[0], row[1], row[2], row[3]
            normalized_date = DailySummaryService._normalize_date(date_value)
            if normalized_date is not None:
                logger.info("Parsed 4-column row with date=%s", normalized_date)
                return normalized_date, value, description, category
            logger.info("Could not normalize 4-column date value from row: %s", row)
            return None

        logger.info("Row below minimum supported length was skipped: %s", row)
        return None

    @staticmethod
    def _normalize_date(raw_value: Any) -> str | None:
        """Normalize supported date formats into ISO YYYY-MM-DD."""
        if raw_value is None:
            logger.info("Date normalization skipped because value is None.")
            return None

        text = str(raw_value).strip()
        if not text:
            logger.info("Date normalization skipped because value is empty.")
            return None

        if text.count("/") == 2:
            try:
                day, month, year = text.split("/")
                iso_date = date(int(year), int(month), int(day)).isoformat()
                logger.info("Normalized Brazilian date %s to %s", text, iso_date)
                return iso_date
            except ValueError:
                logger.info("Could not parse Brazilian date value: %s", text)
                return None

        try:
            iso_date = date.fromisoformat(text).isoformat()
            logger.info("Normalized ISO date %s to %s", text, iso_date)
            return iso_date
        except ValueError:
            logger.info("Could not parse ISO date value: %s", text)
            return None

    @staticmethod
    def _parse_money(raw_value: Any) -> float:
        """Convert money strings like €233.63 or €233,63 into float."""
        text = str(raw_value).strip()
        if not text:
            logger.info("Money parsing skipped because raw value is empty.")
            raise ValueError("Empty monetary value")

        text = text.replace("€", "").replace("£", "").replace("$", "").replace(" ", "")

        if "," in text and "." in text:
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        elif "," in text:
            text = text.replace(",", ".")

        logger.info("Parsed money value %s into %s", raw_value, text)
        return float(text)
