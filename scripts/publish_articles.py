#!/usr/bin/env python3
"""Save and send articles prepared by the Composer agent.

First article is sent immediately; subsequent articles are scheduled
30 minutes apart via Supabase scheduled_at.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.supabase_storage import (
    log_check,
    mark_sent,
    save_articles,
    schedule_articles,
)
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

    immediate, scheduled = schedule_articles(articles, check_slot)
    all_articles = immediate + scheduled

    save_articles(all_articles, check_slot=check_slot)

    if immediate:
        send_alerts(immediate, check_slot=check_slot)
        mark_sent([a["url"] for a in immediate])

    if scheduled:
        for i, article in enumerate(scheduled, start=1):
            when = article["scheduled_at"].strftime("%H:%M UTC")
            print(f"  #{i+1} scheduled at {when} (+{30*i}min): {article['title_fa'][:60]}")

    log_check(check_slot, lookback_hours, articles_found, len(articles))
    print(
        f"Published {len(immediate)} immediately, "
        f"scheduled {len(scheduled)} for later."
    )


if __name__ == "__main__":
    main()
