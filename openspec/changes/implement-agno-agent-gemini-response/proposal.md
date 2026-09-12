## Why

The project needs a lightweight conversational agent pattern that can respond with structured message handling while using Gemini 2.5 Flash Lite as the model provider. This gives the repository a reusable Agno-compatible base that can be extended by the existing finance assistant Telegram and MCP layers.

## What Changes

- Add an Agno-backed agent architecture that can produce message responses through a Gemini 2.5 Flash Lite model.
- Introduce a reusable base agent abstraction inspired by the JARVIS reference implementation in the request.
- Wire the response flow through a message-oriented interface grounded in the current finance assistant project structure.
- Keep the implementation dependency-light by using the project’s existing Python service and config conventions.

## Capabilities

### New Capabilities
- `agno-gemini-response`: Introduce a capability for building and invoking an Agno agent that responds to user messages using Gemini 2.5 Flash Lite.

### Modified Capabilities
- `None`

## Impact

This change affects the Python package structure under the finance assistant source tree, project configuration, and any future Telegram or MCP integrations that need a model-backed response agent. It introduces a new provider-model dependency footprint centered on Agno plus Gemini 2.5 Flash Lite usage.
