"""Telegram message and command handlers."""

import logging

from markdown_it import MarkdownIt
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from finance_assistant.infrastructure.agents.response_agent import FinanceAgent


logger = logging.getLogger(__name__)

finance_agent = FinanceAgent()


def markdown_to_telegram_html(markdown_text: str) -> str:
    """Convert a Markdown-like finance reply into Telegram-safe HTML for the reply handler."""
    if not markdown_text:
        return ""

    parser = MarkdownIt("commonmark", {"breaks": True, "html": False})
    return parser.render(markdown_text)


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
