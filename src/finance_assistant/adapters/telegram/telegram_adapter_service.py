"""Telegram user-to-spreadsheet adapter service."""

from __future__ import annotations


class TelegramAdapterService:
    """Resolve a Telegram user id into a spreadsheet id for the FinanceAgent context."""

    def __init__(self, mapping: dict[int | str, str] | None = None):
        self.user_to_spreadsheet_map = mapping or {
            8910318803: "19HBfcD7gLrvMQFW9RWBezGqtvNh75acAICPevBJWAkY",
            8561890802: "19HBfcD7gLrvMQFW9RWBezGqtvNh75acAICPevBJWAkY",
            5881962910: "1tXN6W9CG57a6aFIWaR9qjo53VBWGYeNd2Sl8Gz9JoLA",
            8363962188: "1XQUab5I1Migodb5RSa6Giz1JhMDD3gLBNyLo94C_zl8",
            1: "18vhWQ3Hy3hDGD9Guii7XUAN2poXBC5erb_lPcFnPzhY",
            5139741753: "12U-jti9ICT3ms9mGKvZwRZiXKstff4m5GlBjcc9i9Rw",
            1660630527: "1Z89pzAaYyvrnF8uKRQlP31et7i2nEZGGeCn-ZJsud78",
            5068170029: "1Xeo8WFCRVx8nwZwwmlFaC9jCOxPUOCZKQo2_QE_QoKE",
            6853832500: "1zTmoe-_-QDn9f64C7lxLNEzjvrlN_173cqJ52WHm7Cg",
        }

    def resolve_spreadsheet_id(self, telegram_user_id: int | str | None) -> str | None:
        """Return a known user's spreadsheet id, or None for unknown ids."""
        if telegram_user_id is None:
            return None

        try:
            normalized_user_id = int(telegram_user_id)
        except (TypeError, ValueError):
            return None

        return self.user_to_spreadsheet_map.get(normalized_user_id)