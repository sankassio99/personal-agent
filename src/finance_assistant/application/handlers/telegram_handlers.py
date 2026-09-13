"""Telegram message and command handlers."""

import logging

from telegram import Update
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
    logger.info("Generated reply will be sent back to Telegram: %s", reply)
    await update.message.reply_text(reply)
