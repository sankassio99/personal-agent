"""Telegram API wrapper used by application services."""

from __future__ import annotations

import asyncio
import inspect
import logging
from concurrent.futures import ThreadPoolExecutor

from finance_assistant.settings import settings
from telegram import Bot

logger = logging.getLogger(__name__)


class TelegramService:
    """Send Telegram messages from synchronous or asynchronous call contexts."""

    def __init__(self, token: str | None = None):
        self.token = token or settings.telegram_token

    def send_message(self, chat_id: int | str | None, text: str) -> dict[str, object]:
        """Send a Telegram message from synchronous or asynchronous call contexts."""
        if chat_id is None:
            raise ValueError("chat_id is required to send the daily summary message.")
        if not self.token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured. Set it in the environment or .env file.")

        logger.info("Sending daily summary to Telegram chat %s", chat_id)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            response = asyncio.run(self._send_message(chat_id, text))
        else:
            with ThreadPoolExecutor(max_workers=1) as executor:
                response = executor.submit(asyncio.run, self._send_message(chat_id, text)).result()

        if isinstance(response, dict):
            message_id = response.get("message_id")
        else:
            message_id = getattr(response, "message_id", None)

        return {"ok": True, "chat_id": chat_id, "text": text, "message_id": message_id}

    async def _send_message(self, chat_id: int | str, text: str):
        """Await Telegram delivery on the event loop that owns the Bot request."""
        bot = Bot(token=self.token)
        response = bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        if inspect.isawaitable(response):
            response = await response
        return response