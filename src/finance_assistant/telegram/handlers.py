"""Telegram message and command handlers."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from finance_assistant.agent.response_agent import GeminiResponseAgent


logger = logging.getLogger(__name__)

STATIC_REPLY = "Hello from your Finance Assistant. I am ready to help you manage your finances."
response_agent = GeminiResponseAgent()


def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    logger.info("Telegram /start command received.")
    update.message.reply_text("Starting")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and reply with the Gemini-backed response adapter."""
    msg = update.message.text or ""
    logger.info("Telegram message received for response processing: %s", msg)
    reply = response_agent.respond(msg)
    logger.info("Generated reply will be sent back to Telegram: %s", reply)
    await update.message.reply_text(reply)
