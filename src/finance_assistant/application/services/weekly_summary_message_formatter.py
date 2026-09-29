"""Formatter for category-grouped weekly expense summaries."""

from __future__ import annotations

from datetime import date
from typing import Any

CATEGORY_EMOJIS = {
    "supermercado": "🛒",
    "commuting": "🚗",
    "transporte": "🚗",
    "compras diversas": "🛍️",
    "extras": "➕",
    "saúde": "💊",
}
DEFAULT_CATEGORY_EMOJI = "🔹"


class WeeklySummaryMessageFormatter:
    """Build the Telegram message for a weekly category summary."""

    def format(self, summary: dict[str, Any]) -> str:
        """Format a weekly summary payload produced by ``WeeklySummaryService``."""
        start_date = self._as_date(summary["start_date"])
        end_date = self._as_date(summary["end_date"])
        period = f"{start_date:%d/%m/%Y} a {end_date:%d/%m/%Y}"
        categories = summary["categories"]

        if not categories:
            return (
                f"📊 <b>Resumo de gastos da semana ({period})</b>:\n\n"
                "Nenhum gasto registrado nesta semana."
            )

        lines = [f"📊 <b>Resumo de gastos da semana ({period})</b>:", ""]
        for item in categories:
            category = str(item["category"])
            emoji = CATEGORY_EMOJIS.get(category.strip().casefold(), DEFAULT_CATEGORY_EMOJI)
            lines.append(f"• {emoji} {category}: €{float(item['total']):.2f}")

        lines.extend(["", f"• 💰 <b>Total da semana</b>: €{float(summary['grand_total']):.2f}"])
        return "\n".join(lines)

    @staticmethod
    def _as_date(value: date | str) -> date:
        """Accept dates from the service and ISO dates for formatter callers."""
        return value if isinstance(value, date) else date.fromisoformat(value)
