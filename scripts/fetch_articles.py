#!/usr/bin/env python3
"""Fetch raw articles as JSON for the Composer agent to process."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import detect_check_slot
from src.news_fetcher import enrich_images, fetch_all_news
from src.supabase_storage import get_sent_urls


def main() -> None:
    check_slot, lookback_hours = detect_check_slot()
    articles = fetch_all_news(lookback_hours=lookback_hours)

    sent_urls = get_sent_urls()
    if sent_urls:
        articles = [a for a in articles if a["url"] not in sent_urls]

    articles = enrich_images(articles)

    output = {
        "check_slot": check_slot,
        "lookback_hours": lookback_hours,
        "articles_found": len(articles),
        "articles": articles,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
