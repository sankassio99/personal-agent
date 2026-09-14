"""Telegram message and command handlers."""

import inspect
from io import BytesIO
import logging
import re
from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.prompts import FINANCE_ASSISTANT_PROMPT
from finance_assistant.infrastructure.agents.response_agent import FinanceAgent
from finance_assistant.infrastructure.agents.speech_to_text_agent import SpeechToTextAgent


logger = logging.getLogger(__name__)

telegram_adapter_service = TelegramAdapterService()
SUMMARY_SPREADSHEET_RANGE = "'Sumário'!B27:F42"
EXPENSES_RANGE_NAME = "'Despesas'!B1:E"
RECURRING_SPREADSHEET_RANGE = "'Recorrentes'!A1:E50"

def build_start_message(telegram_user_id: int | str | None = None) -> str:
    """Return the Telegram start-command onboarding message with admin contact guidance."""
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
        "• Envie seu ID do Telegram e seu e-mail\n"
        "• O administrador criará a planilha no Google Sheets e fará o cadastro no sistema."
    )


def build_unregistered_user_message(telegram_user_id: int | str | None) -> str:
    """Return the friendly admin-contact fallback that mentions the unresolved Telegram user id."""
    return build_start_message(telegram_user_id)


def build_instructions(spreadsheet_id: str | None = None, spreadsheet_range: str | None = None) -> str:
    """Build the FinanceAgent instructions payload using a spreadsheet id and range when available."""
    instructions = FINANCE_ASSISTANT_PROMPT
    today = datetime.now().strftime("%d/%m/%Y")
    instructions += f" The current date is {today}."

    if spreadsheet_id:
        instructions += ". You have access to a Google Sheet with the ID: " + spreadsheet_id + "."

    if spreadsheet_range:
        instructions += " The active spreadsheet range is: " + spreadsheet_range + "."

    return instructions


def build_help_message() -> str:
    """Return a friendly command menu for the Telegram bot."""
    return (
        "📘 Comandos disponíveis:\n"
        "• /start — inicia o cadastro e mostra a orientação de registro\n"
        "• /summary — usa a faixa de planilha do resumo do usuário\n"
        "• /recurring — usa a faixa de planilha recorrente do usuário\n"
        "• /help — mostra esta lista de comandos"
    )


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command with onboarding guidance for spreadsheet registration."""
    logger.info("Telegram /start command received.")

    user = update.effective_user or update.message.from_user
    telegram_user_id = getattr(user, "id", None)
    start_message = build_start_message(telegram_user_id)

    await update.message.reply_text(start_message)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command by returning the list of available Telegram commands."""
    logger.info("Telegram /help command received.")
    await update.message.reply_text(build_help_message())


async def handle_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /summary command by routing through the summary spreadsheet range."""
    logger.info("Telegram /summary command received.")
    msg = update.message.text or ""
    await _dispatch_finance_reply(update, msg, SUMMARY_SPREADSHEET_RANGE)


async def handle_recurring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /recurring command by routing through the recurring spreadsheet range."""
    logger.info("Telegram /recurring command received.")
    msg = update.message.text or ""
    await _dispatch_finance_reply(update, msg, RECURRING_SPREADSHEET_RANGE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and reply with the FinanceAgent-backed response adapter."""
    msg = update.message.text or ""
    logger.info("Telegram message received for response processing: %s", msg)
    await _dispatch_finance_reply(update, msg, EXPENSES_RANGE_NAME)


async def handle_audio_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None or (
        message.voice is None and message.audio is None
    ):
        return

    await message.reply_text("🎙️ Transcribing your audio...")

    try:
        # 1. Download the Telegram audio
        audio = message.voice or message.audio

        telegram_file = await context.bot.get_file(
            audio.file_id
        )

        audio_buffer = BytesIO()
        await telegram_file.download_to_memory(audio_buffer)

        audio_bytes = audio_buffer.getvalue()

        # 2. Transcribe the audio
        speech_agent = SpeechToTextAgent()

        transcript = speech_agent.transcribe(audio_bytes)

        if inspect.isawaitable(transcript):
            transcript = await transcript

        transcript = transcript.strip()

        logger.info("-------------------------------------------------------")
        logger.info("Speech-to-text transcript produced text: %s", transcript)
        logger.info("-------------------------------------------------------")

        if not transcript:
            await message.reply_text(
                "I couldn't recognize your audio. "
                "Please try again."
            )
            return

        # 3. Forward the transcript to your existing finance handler
        await _dispatch_finance_reply(
            update,
            transcript,
            EXPENSES_RANGE_NAME,
        )

    except Exception:
        logger.exception("Failed to process audio message")

        await message.reply_text(
            "Sorry, I couldn't process your audio message."
        )

async def _dispatch_finance_reply(update: Update, message_text: str, spreadsheet_range: str) -> None:
    """Centralize the registration check and finance-agent execution for normal and command replies."""
    user = update.effective_user or update.message.from_user
    telegram_user_id = getattr(user, "id", None)
    spreadsheet_id = telegram_adapter_service.resolve_spreadsheet_id(telegram_user_id)

    if not spreadsheet_id:
        logger.info(
            "Telegram user %s has no spreadsheet mapping; sending admin-registration reply and stopping before FinanceAgent.",
            telegram_user_id,
        )
        await update.message.reply_text(build_unregistered_user_message(telegram_user_id))
        return

    logger.info("Resolved Telegram user %s to spreadsheet %s to range %s", telegram_user_id, spreadsheet_id, spreadsheet_range)

    finance_agent = FinanceAgent(
        instructions=build_instructions(spreadsheet_id, spreadsheet_range),
        spreadsheet_range=spreadsheet_range,
    )
    reply = finance_agent.respond(message_text)
    reply_html = markdown_to_telegram_html(reply)
    logger.info("Generated reply will be sent back to Telegram as HTML: %s", reply_html)
    await update.message.reply_text(reply_html, parse_mode=ParseMode.HTML)


# Move to another file further
def markdown_to_telegram_html(markdown_text: str) -> str:
    """Convert a Markdown-like finance reply into Telegram-safe HTML for the reply handler."""
    if not markdown_text:
        return ""

    # Convert bullet points before applying other Markdown-like transformations.
    markdown_text = re.sub(r"(?m)^\* (.+)", r" • \1", markdown_text)

    # Bold: **text** or __text__
    markdown_text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", markdown_text)
    markdown_text = re.sub(r"__(.+?)__", r"<b>\1</b>", markdown_text)

    # Italic: *markdown_text* or _markdown_text_.
    # Do not let a bullet marker `* ` be interpreted as an italic opener.
    markdown_text = re.sub(r"(?<!\*)\*(?!\*|\s)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", markdown_text)
    markdown_text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<i>\1</i>", markdown_text)

    # Remove hashtags, including groups like ###word and ##otherword
    markdown_text = re.sub(r"(?<!\w)#+([^\s#]+)", r"\1", markdown_text)

    return markdown_text