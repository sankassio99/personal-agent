"""Shared Telegram user-facing message builders."""

from __future__ import annotations


def build_start_message(telegram_user_id: int | str | None = None) -> str:
    """Return onboarding guidance for registered or unregistered users."""
    if telegram_user_id is None:
        return (
            "👋 Bem-vindo(a) ao Finance Assistant!\n\n"
            "Para começar, siga estes passos:\n"
            "• Entre em contato com o administrador @kassiodev\n"
            "• Envie seu ID do Telegram e seu e-mail\n"
            "• O administrador criará a planilha no Google Sheets e fará o cadastro no sistema."
        )

    return (
        f"👋 Bem-vindo(a) ao Finance Assistant!\n\n"
        f"📄 Ainda não há uma planilha cadastrada para o usuário do Telegram {telegram_user_id}.\n\n"
        "Para continuar, siga estes passos:\n"
        "• Entre em contato com o administrador @kassiodev\n"
        "• Envie seu ID do Telegram {telegram_user_id} e seu e-mail\n"
        "• O administrador criará a planilha no Google Sheets e fará o cadastro no sistema."
        "Caso já tenha sido cadastradas, digite /ajuda para ver os comandos disponíveis."
    )


def build_help_message() -> str:
    """Return the available Telegram commands."""
    return (
        "📘 Comandos disponíveis:\n"
        "• /start — inicia o cadastro e mostra a orientação de registro\n"
        "• /sumario — usa a faixa de planilha do resumo do usuário\n"
        "• /recorrente — usa a faixa de planilha recorrente do usuário\n"
        "• /rendimentos — consulta e registra rendimentos do usuário\n"
        "• /ajuda — mostra esta lista de comandos"
    )


def build_unregistered_user_message(telegram_user_id: int | str | None) -> str:
    """Return onboarding guidance for an unresolved Telegram user."""
    return build_start_message(telegram_user_id)