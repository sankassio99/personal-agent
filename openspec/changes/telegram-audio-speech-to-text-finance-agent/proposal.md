## Why

The current Telegram integration only accepts text messages and routes them directly to the finance assistant. Audio or voice messages from Telegram are not handled by the handler registry, so the workflow cannot convert spoken expense requests into the same finance agent context that text requests already use.

## What Changes

- Add an audio-aware Telegram message path that recognizes Telegram voice and audio attachments.
- Introduce a speech-to-text agent grounded in the Agno/Gemini pattern described in the repository guidance and the provided speech-to-text instructions.
- Transcribe the audio payload into text and then send that transcript into the existing finance reply pipeline.
- Preserve the existing user registration and spreadsheet-range routing checks before the finance agent runs.

## Capabilities

### New Capabilities
- `telegram-audio-transcription`: Accept Telegram audio messages, transcribe spoken content into plain text, and deliver that transcript into the finance response flow.

### Modified Capabilities
- None.

## Impact

Affected code will be centered in the Telegram adapter and handler layer, plus the finance agent orchestration service that currently assumes plain text input. The project may reuse the existing Gemini-backed Agno model stack and introduction of a lightweight transcription agent service instead of creating a separate external dependency.
