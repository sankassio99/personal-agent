## Context

The repository already has a Python package centered on finance assistant flows and Telegram event processing, but it does not yet expose a reusable Agno base agent or a Gemini-backed response adapter. The requested implementation should adopt the structure demonstrated in the JARVIS reference base agent: one base class creates an Agno `Agent` using a `Gemini` model selection configured via the repository’s settings object.

The repository currently uses a static Telegram handler and a simple module layout, so the new capability should remain additive. The design should keep the model dependency localized to a service or agent adapter rather than forcing a large rewrite of the Telegram or MCP layers.

## Goals / Non-Goals

**Goals:**
- Add a reusable base agent contract that creates an Agno `Agent` around a `Gemini` configuration.
- Support a Gemini 2.5 Flash Lite message-generation path for response-style flows.
- Keep the pattern compatible with the existing finance assistant repository anatomy and environment-driven configuration.

**Non-Goals:**
- Replacing the Telegram runtime or MCP server architecture.
- Persisting long-term conversation memory through the scope of this proposal.
- Implementing advanced tool-calling, retrieval, or external knowledge layers beyond the requested message response pattern.

## Decisions

1. Create a `BaseAgent` abstraction in the agent package that wraps `agno.agent.Agent` with a `Gemini` model object. This mirrors the JARVIS `BaseAgent` idea while adapting it to the finance assistant module layout.

   Rationale: the repository already has an `agent/` module namespace. Centralizing an `Agent` factory in a base contract reduces duplicate configuration and keeps the dependency on Agno and Gemini explicit instead of hidden in handlers.

   Alternatives considered: placing model initialization directly in each bot or handler, or introducing a new agent package outside of the current repository convention. The base abstraction avoids both and makes the implementation composable.

2. Use an environment-configurable Gemini model reference, defaulting to `gemini-2.5-flash-lite` in code and leaving the actual API key in configuration. The design should make the invocation path easy to plug into a future response agent class in the same style as the JARVIS reference.

   Rationale: this satisfies the requested capability without overfitting the existing finance assistant package. It also respects the repository’s current configuration strategy through environment variables and a settings module.

   Alternatives considered: hardcoding a model ID in the Telegram handler or requiring multiple model-specific packages. The model should remain a dependency of the agent layer, not a per-message controller detail.

3. Use the base agent as the seam for future message processors rather than coupling the Telegram handler directly to the model SDK. The handler should keep receiving and formatting a user message, while the agent adapter should produce the response string.

   Rationale: this creates a separation between transport concerns and LLM response concerns and aligns the local project architecture with a service-oriented design.

   Alternatives considered: injecting the model directly into the handler or the MCP server. That would pull model concerns into transport code and make testing much harder.

## Risks / Trade-offs

- [Model dependency drift] ? Keep the model ID and dependency set in a central settings location so upgrades to Gemini versions are easy to manage.
- [Configuration fragility] ? Require `GEMINI_API_KEY` and model environment variables to be present before attempting model initialization.
- [Transport coupling] ? Avoid adding model SDK imports to Telegram or MCP routing code; keep the usage behind an agent adapter object.

## Migration Plan

1. Add the new `BaseAgent` pattern in the agent package structure.
2. Add or document the environment variable path where the Gemini API key is read.
3. Use the Telegram or MCP adapters to call the model response wrapper, keeping the current static reply as a fallback.
4. Verify the package imports and agent factory setup without introducing regressions to the finance assistant workflow.

## Open Questions

- Should the repository prefer a direct Agno `Gemini` model import or a string-based model provider registry for future model swaps?
- Should the new response wrapper be exposed through the existing `src/finance_assistant/agent/` namespace or through a new `services/` package under the same project? 
