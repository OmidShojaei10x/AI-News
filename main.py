"""Utilities for AI news check scheduling.

This project is designed to run via Cursor Automation (Composer).
The agent fetches articles, filters importance, translates to Persian,
then publishes via scripts/publish_articles.py.

See AUTOMATION_PROMPT.md for the full workflow.
"""

import pytz
from datetime import datetime

SLOT_WINDOWS = {
    "morning": (8 * 60 + 45, 9 * 60 + 30, 24),
    "noon": (11 * 60 + 45, 12 * 60 + 30, 8),
    "evening": (20 * 60 + 45, 21 * 60 + 30, 8),
}


def detect_check_slot() -> tuple[str, int]:
    """Return (check_slot, lookback_hours) based on Tehran time."""
    import os

    override = os.environ.get("CHECK_SLOT", "").strip().lower()
    if override in SLOT_WINDOWS:
        _, _, lookback = SLOT_WINDOWS[override]
        return override, lookback

    tehran = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran)
    minutes = now.hour * 60 + now.minute

    for slot, (start, end, lookback) in SLOT_WINDOWS.items():
        if start <= minutes <= end:
            return slot, lookback

    if minutes < 11 * 60 + 45:
        return "morning", 24
    if minutes < 20 * 60 + 45:
        return "noon", 8
    return "evening", 8
