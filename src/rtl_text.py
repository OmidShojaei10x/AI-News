"""Bidirectional text helpers for Persian Telegram messages with embedded Latin."""

import re

# Unicode directional marks
RLM = "\u200f"  # Right-to-Left Mark — sets base direction
LRI = "\u2066"  # Left-to-Right Isolate — wraps Latin runs
PDI = "\u2069"  # Pop Directional Isolate

# Latin/technical runs inside Persian text (brand names, model IDs, URLs fragments)
_LATIN_RUN = re.compile(
    r"[A-Za-z][\w\-./+#@&%$]*(?:\s+[A-Za-z][\w\-./+#@&%$]*)*"
    r"|"
    r"\$[\d,.]+[BMK]?"
    r"|"
    r"[\d]+(?:\.\d+)?\s*(?:B|M|K|billion|million|USD|GB|TB)\b",
    re.IGNORECASE,
)

# HTML tags must not be altered
_HTML_TAG = re.compile(r"<[^>]+>")


def _isolate_latin_segment(text: str) -> str:
    """Wrap Latin segments with LRI/PDI so they render LTR inside RTL text."""

    def _wrap(match: re.Match[str]) -> str:
        segment = match.group(0)
        return f"{LRI}{segment}{PDI}"

    return _LATIN_RUN.sub(_wrap, text)


def fix_rtl(text: str) -> str:
    """Prepare mixed Persian/Latin text for correct RTL display in Telegram."""
    if not text:
        return text

    if text.startswith(RLM):
        return text

    parts: list[str] = []
    last_end = 0
    for match in _HTML_TAG.finditer(text):
        if match.start() > last_end:
            parts.append(_isolate_latin_segment(text[last_end : match.start()]))
        parts.append(match.group(0))
        last_end = match.end()

    if last_end < len(text):
        parts.append(_isolate_latin_segment(text[last_end:]))

    body = "".join(parts) if parts else _isolate_latin_segment(text)
    return RLM + body
