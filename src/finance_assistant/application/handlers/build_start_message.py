"""Build the Telegram onboarding message."""

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