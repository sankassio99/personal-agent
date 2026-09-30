"""Shared Telegram user-facing message builders."""

from __future__ import annotations


def build_start_message(telegram_user_id: int | str | None = None) -> str:
    """Return the welcome message shown by the /start command."""
    return (
        "Olá! 👋\n\n"
        "O Assistente de Finanças ajuda você a organizar sua vida financeira "
        "de forma simples pelo Telegram.\n\n"
        "Principais utilidades:\n"
        "• Registrar despesas e rendimentos por mensagem ou áudio;\n"
        "• Consultar gastos recentes e categorias disponíveis;\n"
        "• Acompanhar o resumo financeiro;\n"
        "• Controlar lançamentos recorrentes;\n"
        "• Receber um resumo diário das movimentações;\n"
        "• Ser avisado quando uma categoria estiver próxima ou acima do "
        "orçamento definido.\n\n"
        "Basta enviar uma mensagem como: “Gastei 25€ no supermercado” e o "
        "assistente organiza o lançamento para você.\n\n"
        "Para começar, envie /instrucoes."
    )


def build_unregistered_user_message(telegram_user_id: int | str | None) -> str:
    """Return registration guidance for an unresolved Telegram user."""
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
        f"• Envie seu ID do Telegram {telegram_user_id} e seu e-mail\n"
        "• O administrador criará a planilha no Google Sheets e fará o cadastro no sistema."
        "Caso já tenha sido cadastradas, digite /ajuda para ver os comandos disponíveis."
    )


def build_instructions_message() -> str:
    """Return a simple step-by-step guide for requesting access."""
    return (
        "📋 Como começar\n\n"
        "Siga estes passos para usar o Assistente de Finanças:\n"
        "• Fale com o administrador @kassiodev.\n"
        "• Envie seu ID do Telegram e seu e-mail.\n"
        "• Aguarde a criação da sua planilha e a confirmação do cadastro.\n"
        "• Depois, envie /ajuda para conhecer os comandos disponíveis."
    )


def build_help_message() -> str:
    """Return the available Telegram commands."""
    return (
        "📘 Comandos disponíveis:\n"
        "• /start — apresenta o Assistente de Finanças\n"
        "• /instrucoes — mostra como solicitar acesso ao assistente\n"
        "• /sumario — usa a faixa de planilha do resumo do usuário\n"
        "• /recorrente — usa a faixa de planilha recorrente do usuário\n"
        "• /rendimentos — consulta e registra rendimentos do usuário\n"
        "• /ajuda — mostra esta lista de comandos"
    )
