"""Telegram message and command handlers."""

from telegram import Update
from telegram.ext import ContextTypes

STATIC_REPLY = "Hello from your Finance Assistant. I am ready to help you manage your finances."


def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    update.message.reply_text("Starting")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and reply with a static response."""
    await update.message.reply_text(STATIC_REPLY)
