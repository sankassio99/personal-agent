"""Handle Telegram audio and voice messages."""

from __future__ import annotations

import inspect
from io import BytesIO

from finance_assistant.application.handlers.message_handler import EXPENSES_SPREADSHEET_RANGE
from finance_assistant.application.handlers.build_instructions import build_instructions
from finance_assistant.application.handlers.build_unregistered_user_message import build_unregistered_user_message
from finance_assistant.application.handlers.markdown_to_telegram_html import markdown_to_telegram_html
from finance_assistant.application.services.telegram_adapter_service import TelegramAdapterService
from finance_assistant.infrastructure.agents.add_expense_tool import telegram_user_context
from finance_assistant.infrastructure.agents.response_agent import FinanceAgent
from finance_assistant.infrastructure.agents.speech_to_text_agent import SpeechToTextAgent
from telegram.constants import ParseMode

async def handle_audio_message(update, context) -> None:
    """Download audio, transcribe it, and forward the transcript to finance processing."""
    message = update.effective_message
    if message is None or (message.voice is None and message.audio is None):
        return

    await message.reply_text("🎙️ Transcribing your audio...")

    try:
        audio = message.voice or message.audio
        telegram_file = await context.bot.get_file(audio.file_id)
        audio_buffer = BytesIO()
        await telegram_file.download_to_memory(audio_buffer)

        transcript = SpeechToTextAgent().transcribe(audio_buffer.getvalue())
        if inspect.isawaitable(transcript):
            transcript = await transcript
        transcript = transcript.strip()

        if not transcript:
            await message.reply_text("I couldn't recognize your audio. Please try again.")
            return

        user = update.effective_user or update.message.from_user
        telegram_user_id = getattr(user, "id", None)
        spreadsheet_id = TelegramAdapterService().resolve_spreadsheet_id(telegram_user_id)

        if not spreadsheet_id:
            await message.reply_text(build_unregistered_user_message(telegram_user_id))
            return

        finance_agent = FinanceAgent(
            instructions=build_instructions(spreadsheet_id, EXPENSES_SPREADSHEET_RANGE),
            spreadsheet_range=EXPENSES_SPREADSHEET_RANGE,
        )
        with telegram_user_context(telegram_user_id):
            reply = finance_agent.respond(transcript)

        await message.reply_text(markdown_to_telegram_html(reply), parse_mode=ParseMode.HTML)
    except Exception:
        await message.reply_text("Sorry, I couldn't process your audio message.")