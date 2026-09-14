## 1. Telegram audio intake

- [ ] 1.1 Extend the Telegram bot register and handler path to recognize audio and voice message filters without dropping the existing text command path.
- [ ] 1.2 Add a Telegram audio normalization helper that extracts the audio bytes from `update.message.audio`, `update.message.voice`, or a Telegram file object and returns a binary payload for transcription.

## 2. Speech-to-text adapter

- [ ] 2.1 Add a lightweight transcription service that mirrors the documented Agno/Gemini audio-to-text example by constructing an `Agent(model=Gemini(...))` and passing `Audio(content=audio_content)`.
- [ ] 2.2 Convert the audio transcript to plain text and return a clean string for the next finance-step routing.

## 3. Finance route reuse

- [ ] 3.1 Wire the transcript into the existing registration-aware `_dispatch_finance_reply` flow so the spreadsheet id and spreadsheet range checks remain the single entry gate.
- [ ] 3.2 Reuse the existing Markdown-to-HTML formatting and reply flow so the user receives the same HTML reply behavior after transcription.

## 4. Validation

- [ ] 4.1 Add a regression test for the audio path that confirms an audio update is transcribed and then handed to `FinanceAgent.respond` with the same user guard constraints as regular text messages.
- [ ] 4.2 Verify the new change does not break the existing `/start`, `/summary`, `/recurring`, and `/help` command message registration behavior.
