"""Build the Telegram help message."""


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