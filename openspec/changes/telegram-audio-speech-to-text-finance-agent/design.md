## Context

The current Telegram integration in the finance assistant routes normal text messages through the finance handler and uses the `FinanceAgent` adapter to answer questions against the user’s spreadsheet context. There is no audio-aware branch in the adapter, and the Telegram bot is registered only for `filters.TEXT & ~filters.COMMAND`.

The attached speech-to-text guidance recommends the Agno/Gemini pattern for audio transcription: build an `Agent` with `Gemini(id="gemini-2.0-flash-exp")`, attach an `Audio` payload, and ask the model to produce a transcript. This project already uses Agno-backed Gemini model objects through `BaseAgent`, so the design should reuse the same model strategy from a dedicated transcription service.

## Goals / Non-Goals

**Goals:**
- Accept Telegram voice and audio message payloads.
- Extract the audio bytes from the update object and normalize them into a transcription request.
- Send the transcribed plain-text result into the same registered-user and spreadsheet-range routing path used by the finance handler.
- Keep the existing finance response formatting and HTML reply conversion intact for the user.

**Non-Goals:**
- Replacing the finance agent’s spreadsheet tools or Google Sheets integration.
- Handling arbitrary multimedia types beyond Telegram audio/voice messages.
- Introducing a new external transcription service or a separate command-level UX model.

## Decisions

1. The bot will detect Telegram audio messages in the same message handling layer as text messages, but route the audio object to a new transcription adapter before sending the transcript to `FinanceAgent`.
   - Rationale: This preserves the existing Telegram command structure and avoids changing the spreadsheet-range contract already enforced in `_dispatch_finance_reply`.
   - Alternatives considered: Add a brand-new Telegram-specific command (`/audio`) or bypass the finance agent entirely with a plain transcription response. Both would undermine the desired finance workflow and would not satisfy the “send to finance agent” requirement.

2. The transcription component will be an `Agno`-style `Agent` that uses the repository’s `Gemini` model object and receives `Audio(content=<bytes>)` payloads.
   - Rationale: This is consistent with the documentation snippet and with the project’s existing dependency model (`agno`, `google-genai`, `Gemini`).
   - Alternatives considered: Use `OpenAI` or `Whisper` APIs requiring another service or environment-specific API credentials. This project already centers on Gemini-backed agents and should minimize extra dependencies.

3. The transcription result will be forwarded to the existing `_dispatch_finance_reply` method as a normalized string so the same registration and range fallback behavior remains intact.
   - Rationale: The user’s spreadsheet mapping and `spreadsheet_range` resolution remain the security and route gate before the finance agent is invoked.
   - Alternatives considered: Bypass user mapping or call `FinanceAgent` without a mapping check. That would create a path that does not enforce the project’s current registration contract.

4. Audio replies should be buffered and transcribed lazily as plain text, then cleaned of speaker labels or formatting metadata to keep the transcript usable by the finance agent.
   - Rationale: The audio-to-text example suggests a transcript focused on normal conversation text. The finance requirements already expect natural language commands and expense expressions.
   - Alternatives considered: Forward raw audio metadata or a verbose multimodal transcript. That would add noise to the expense workflow and create an unstable prompt string for the finance agent.

## Risks / Trade-offs

- [Risk] Telegram audio payloads may arrive as `voice` objects or file objects with different MIME metadata. → Mitigation: Normalize `update.message.voice` and `update.message.audio` into an input stream buffer and pass raw bytes to the transcription agent.
- [Risk] Large audio objects may exceed the Telegram update transport or memory assumptions. → Mitigation: Accept only the file bytes provided by Python Telegram Bot and keep transcription execution in a background-friendly agent adapter rather than inside `reply_text` handling.
- [Risk] The Gemini transcription path may produce a low-confidence transcript in noisy messages. → Mitigation: Add a default prompt that requests the concise transcript and trims non-finance-labeled output before dispatch.

## Migration Plan

1. Extend the Telegram handler registration to accept audio or voice messages through the Python Telegram Bot `filters` chain.
2. Add a transcription adapter module that creates an Agno `Agent` using the repository’s existing Gemini model pattern and returns a plain transcript.
3. Refactor `_dispatch_finance_reply` or create a wrapper that accepts either a text message or a transcript and preserves the spreadsheet mapping check before the finance agent executes.
4. Verify the flow with an end-to-end test that sends a Telegram audio payload through a mock update object and observes the transcript passing into `FinanceAgent.respond`.

## Open Questions

- Should the transcription step be synchronous or asynchronous in the current bot event loop, especially for long audio files?
- Will the project treat Telegram voice messages as a transcription-only input or also allow regular audio files (`audio` objects) with the same fallback path?
- Should the transcript prompt explicitly instruct the model to include only request text and remove all filler terms?
