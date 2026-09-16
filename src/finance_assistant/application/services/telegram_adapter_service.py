"""Telegram user-to-spreadsheet adapter service."""

from __future__ import annotations


class TelegramAdapterService:
    """Resolve a Telegram user id into a spreadsheet id for the FinanceAgent context.

    The repository currently favors a lightweight in-memory registry as a first
    implementation boundary. This gives the Telegram flow a single place to
    normalize the Telegram user id and perform a safe unknown-user fallback.
    """

    def __init__(self, mapping: dict[int | str, str] | None = None):
        self.user_to_spreadsheet_map = mapping or {
            8910318803: "19HBfcD7gLrvMQFW9RWBezGqtvNh75acAICPevBJWAkY", # Kassio
            5881962910: "1tXN6W9CG57a6aFIWaR9qjo53VBWGYeNd2Sl8Gz9JoLA", # Leti
            8363962188: "1XQUab5I1Migodb5RSa6Giz1JhMDD3gLBNyLo94C_zl8", # Mari
            1561890802: "1ZaCfOuVdHa3H_Q7_UloP467jvA6r9BMgttIzeqxSouM", # Cassia Teste
            1561890802: "18vhWQ3Hy3hDGD9Guii7XUAN2poXBC5erb_lPcFnPzhY", # Tomaz
            5139741753: "12U-jti9ICT3ms9mGKvZwRZiXKstff4m5GlBjcc9i9Rw", # Crisley
        }

    def resolve_spreadsheet_id(self, telegram_user_id: int | str | None) -> str | None:
        """Return the spreadsheet id for a known Telegram user, or None if unknown.

        Unknown or malformed ids degrade safely by returning None instead of
        forcing the handler to boot the agent with an unrelated spreadsheet.
        """
        if telegram_user_id is None:
            return None

        try:
            normalized_user_id = int(telegram_user_id)
        except (TypeError, ValueError):
            return None

        return self.user_to_spreadsheet_map.get(normalized_user_id)
