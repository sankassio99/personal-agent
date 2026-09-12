## Implementation Tasks

1. Add a reusable `BaseAgent` abstraction under the finance assistant agent package that wraps the Agno `Agent` class and injects a configured Gemini `Gemini(id="gemini-2.5-flash-lite", api_key=Config.GEMINI_API_KEY)` model object.
2. Add a response adapter or message processor entry point that accepts an incoming user message string and returns a deterministic same-channel response string through the Agno `Agent.run()` flow.
3. Allow the environment/configuration layer to read or validate the `GEMINI_API_KEY` value and surface a clean configuration error when the key is missing.
4. Keep the transport integration contract intact by routing the message response through an adapter boundary instead of placing the `Gemini` object directly in the Telegram handler or MCP server.
5. Add a regression-style test for the new response agent contract: build the `BaseAgent` factory and ensure the created `Agent` receives the configured model and instructions object.
