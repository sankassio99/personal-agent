"""Handle Telegram audio and voice messages."""

from __future__ import annotations

import inspect
from io import BytesIO

from finance_assistant.application.handlers.finance_reply_dispatcher import _build_dispatcher
from finance_assistant.application.handlers.message_handler import EXPENSES_SPREADSHEET_RANGE
from finance_assistant.infrastructure.agents.speech_to_text_agent import SpeechToTextAgent

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

        await _build_dispatcher().dispatch(update, transcript, EXPENSES_SPREADSHEET_RANGE)
    except Exception:
        await message.reply_text("Sorry, I couldn't process your audio message.")