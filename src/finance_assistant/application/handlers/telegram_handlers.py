"""Telegram message and command handlers."""

import logging
import re

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from finance_assistant.infrastructure.agents.response_agent import FinanceAgent


logger = logging.getLogger(__name__)

finance_agent = FinanceAgent()


def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    logger.info("Telegram /start command received.")
    update.message.reply_text("Starting")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and reply with the FinanceAgent-backed response adapter."""
    msg = update.message.text or ""
    logger.info("Telegram message received for response processing: %s", msg)
    reply = finance_agent.respond(msg)
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