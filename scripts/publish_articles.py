#!/usr/bin/env python3
"""Save and send articles prepared by the Composer agent."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.supabase_storage import log_check, mark_sent, save_articles
from src.telegram_sender import send_alerts


def main() -> None:
    data = json.load(sys.stdin)
    check_slot = data["check_slot"]
    lookback_hours = data["lookback_hours"]
    articles_found = data.get("articles_found", 0)
    articles = data.get("articles", [])

    if not articles:
        log_check(check_slot, lookback_hours, articles_found, 0)
        print("No articles to publish.")
        return

    save_articles(articles, check_slot=check_slot)
    send_alerts(articles, check_slot=check_slot)
    mark_sent([a["url"] for a in articles])
    log_check(check_slot, lookback_hours, articles_found, len(articles))
    print(f"Published {len(articles)} article(s).")


if __name__ == "__main__":
    main()
