"""Convert finance-agent Markdown-like output to Telegram HTML."""

from __future__ import annotations

import re


def markdown_to_telegram_html(markdown_text: str) -> str:
    """Convert supported Markdown-like formatting into Telegram-safe HTML."""
    if not markdown_text:
        return ""

    markdown_text = re.sub(r"(?m)^\* (.+)", r" • \1", markdown_text)
    markdown_text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", markdown_text)
    markdown_text = re.sub(r"__(.+?)__", r"<b>\1</b>", markdown_text)
    markdown_text = re.sub(r"(?<!\*)\*(?!\*|\s)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", markdown_text)
    markdown_text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<i>\1</i>", markdown_text)
    markdown_text = re.sub(r"(?<!\w)#+([^\s#]+)", r"\1", markdown_text)

    return markdown_text