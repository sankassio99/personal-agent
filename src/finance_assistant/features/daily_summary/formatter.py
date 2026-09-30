"""Format daily summary rows for Telegram."""

from __future__ import annotations

from datetime import date


class DailySummaryMessageFormatter:
    """Build the HTML message shown to Telegram users for a daily summary."""

    def format(self, rows: list[dict[str, object]], current_date: date) -> str:
        """Format the summary rows into a Telegram-friendly HTML message."""
        if not rows:
            return "📋 <b>Resumo de Gastos de Hoje</b>:\n\nNenhum gasto registrado para hoje."

        total = sum(float(row["value"]) for row in rows)
        today = current_date.strftime("%d/%m/%Y")

        lines = [
            f"📋 <b>Resumo de Gastos de Hoje ({today})</b>:",
            "",
        ]

        for row in rows:
            lines.append(f"•  {row['description']}: €{float(row['value']):.2f} ({row['category']})")

        lines.extend(["", f"💰 <b>Total gasto hoje</b>: €{total:.2f}"])
        return "\n".join(lines)