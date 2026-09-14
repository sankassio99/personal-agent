## ADDED Requirements

### Requirement: Telegram audio messages may be transcribed and forwarded to the finance agent
The system SHALL accept Telegram audio and voice-message payloads, use an Agno/Gemini audio-to-text agent pattern to convert the audio bytes into a text transcript, and send that transcript to the existing finance agent flow after user registration and spreadsheet-range resolution.

#### Scenario: Audio message triggers transcript path
- **WHEN** a user sends an audio or voice message through Telegram
- **THEN** the system SHALL fetch the audio payload, pass it to the speech-to-text agent, and produce a plain-text transcript that can be forwarded to the finance response adapter.

#### Scenario: Transcript is routed through the finance agent context
- **WHEN** the speech-to-text transcript is ready
- **THEN** the system SHALL verify the Telegram user is mapped to a spreadsheet and then route the transcript through the same finance agent and spreadsheet range resolution path already used by text messages.

#### Scenario: Unsupported or missing audio payload is handled safely
- **WHEN** a Telegram update does not contain an audio or voice payload or the payload cannot be read
- **THEN** the system SHALL return a handled fallback message instead of sending an empty or broken transcript to the finance agent.
