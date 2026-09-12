## Implementation Tasks

- [x] 1. Create a reusable `BaseAgent` abstraction in the finance assistant agent package that wraps the Agno `Agent` class and initializes a Gemini model object using the configured settings object.
- [x] 2. Add a `GeminiResponseAgent` wrapper that accepts an incoming message and returns a string response through the Agent-like `run()` flow.
- [x] 3. Extend the repository settings object so the Gemini API key and Gemini model identifier are read from environment configuration without touching the Telegram handler.
- [x] 4. Keep the transport integration contract intact by introducing a response adapter seam rather than placing model code directly in the existing message entrypoint.
- [x] 5. Add a regression-style unit test that exercises the new model-backed agent factory and message response adapter contract.
