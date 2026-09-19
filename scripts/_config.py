import os
from datetime import datetime

import pytz

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def current_slot() -> tuple[str, int]:
    """Return (slot_name, lookback_hours) based on Tehran time."""
    tehran = pytz.timezone("Asia/Tehran")
    hour = datetime.now(tehran).hour
    if 8 <= hour < 11:
        return "morning", 24
    if 11 <= hour < 18:
        return "noon", 8
    return "evening", 8
