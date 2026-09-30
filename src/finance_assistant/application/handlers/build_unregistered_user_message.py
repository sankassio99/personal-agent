"""Build the response shown to users without a spreadsheet mapping."""

from __future__ import annotations

from finance_assistant.application.handlers.build_start_message import build_start_message


def build_unregistered_user_message(telegram_user_id: int | str | None) -> str:
    """Return onboarding guidance for an unresolved Telegram user."""
    return build_start_message(telegram_user_id)