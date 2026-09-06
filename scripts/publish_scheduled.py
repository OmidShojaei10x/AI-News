#!/usr/bin/env python3
"""Publish articles whose scheduled_at time has passed."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.supabase_storage import get_due_scheduled_articles, mark_sent
from src.telegram_sender import send_article


def main() -> None:
    due = get_due_scheduled_articles()
    if not due:
        print("No scheduled articles due.")
        return

    sent_urls = []
    for article in due:
        print(f"Sending scheduled: {article['title_fa'][:60]}...")
        if send_article(article):
            sent_urls.append(article["url"])
        else:
            print(f"  Failed to send: {article['url']}")

    if sent_urls:
        mark_sent(sent_urls)
        print(f"Published {len(sent_urls)} scheduled article(s).")


if __name__ == "__main__":
    main()
