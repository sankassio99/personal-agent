## Context

The finance assistant Telegram integration currently builds a reply in the application handler by calling the finance agent and sending the text response back with `parse_mode=MARKDOWN`. The implementation path is in the repository’s `finance_assistant.application.handlers.telegram_handlers` and relies on a shared response adapter. The request calls for a new dependency-free conversion strategy that transforms the structured reply into an HTML-safe Telegram payload while keeping the response agent and adapter API stable.

## Goals / Non-Goals

**Goals:**
- Route Telegram replies through an HTML-capable formatter without changing the finance agent contract.
- Preserve a clear normalization boundary in the Telegram handler.
- Keep Markdown / plain text responses sending cleanly through a single transformation utility.

**Non-Goals:**
- Rewriting the upstream finance agent prompt pipelines.
- Introducing a new agent framework or changing the Telegram bot command model.
- Requiring full rich-text support for every response fragment.

## Decisions

1. HTML conversion will be performed in the Telegram application handler immediately before sending the `reply_text` payload, so the existing agent remains the source of the reply text.

   Rationale: This is the least invasive place to change formats because the handler owns the `parse_mode` negotiation with the Telegram library. It also reinforces a clear seam where Markdown-like content can be serialized to HTML without changing the response agent’s domain contract.

2. The implementation will use the `markdown-it-py` ecosystem, which exposes a Python Markdown parser/tokenizer that can be adapted to HTML output. The conversion layer will preserve safe Telegram HTML escapes and only emit allowed formatting elements.

   Rationale: The repository already depends on a Markdown-backed message pipeline. A Markdown parser that has a stable HTML rendering path is safer than trying to force raw HTML from the agent. It also provides a predictable path to convert Markdown lists, emphasis, and headings into Telegram-safe HTML.

3. The Telegram reply will use `telegram.constants.ParseMode.HTML` and the handler will call `reply_text` with the converted HTML string instead of `MARKDOWN`.

   Rationale: Telegram’s HTML parser requires a different escaping and tag structure than Markdown. Switching the parse mode aligns message delivery with the HTML string created by the converter and avoids mixed parse semantics.

## Risks / Trade-offs

- [Risk] Telegram HTML is stricter than Markdown and can easily break on unescaped user content. → Mitigation: The conversion path should escape raw text nodes and only allow safe inline tags produced by the parser.
- [Risk] Some Markdown syntax may not map one-to-one to Telegram HTML. → Mitigation: Limit the supported subset in the conversion utility to common inline emphasis, lists, and basic paragraphs.
- [Risk] The dependency introduces another formatter surface. → Mitigation: Keep the conversion utility isolated in the application or infra transport layer so the finance agent remains unchanged.

## Migration Plan

1. Add the formatter utility and wire the Telegram handler to call it.
2. Update dependency metadata so the project can import the Markdown parser package.
3. Verify the HTML conversion path in a controlled path and then update the parse mode from Markdown to HTML.
4. Roll back by switching the parse mode back to Markdown if the converter cannot safely encode a message.

## Open Questions

- Whether the converter should aim for a full Markdown-to-HTML rendering pass or a small supported subset.
- Whether the HTML string needs to be sanitized further for Telegram’s strict HTML renderer.
