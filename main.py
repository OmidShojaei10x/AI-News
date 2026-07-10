import os
import sys
from datetime import datetime

import pytz


def _is_tehran_send_window() -> bool:
    """Return True if Tehran clock is in the 07:45–08:30 window."""
    tehran = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran)
    minutes = now.hour * 60 + now.minute
    return (7 * 60 + 45) <= minutes <= (8 * 60 + 30)


def run_digest() -> None:
    """Fetch, process, and send the daily AI news digest."""
    from src.news_fetcher import fetch_all_news
    from src.news_processor import process_news
    from src.telegram_sender import send_daily_digest

    print("── Step 1: Fetching AI news from the last 24 hours ──")
    articles = fetch_all_news()
    print(f"Total unique articles: {len(articles)}")

    if not articles:
        print("No articles found. Exiting.")
        return

    print("\n── Step 2: Processing & translating with Gemini ──")
    processed = process_news(articles)
    print(f"Selected top {len(processed)} articles")

    if not processed:
        print("No articles after processing. Exiting.")
        return

    print("\n── Step 3: Sending to Telegram ──")
    send_daily_digest(processed)
    print("\n✓ Daily AI news digest sent successfully!")


def main() -> None:
    force = os.environ.get("FORCE_SEND", "false").lower() == "true"
    # GITHUB_EVENT_NAME is set when running inside GitHub Actions
    github_event = os.environ.get("GITHUB_EVENT_NAME", "")

    skip_check = force or github_event == "workflow_dispatch"
    if not skip_check and github_event != "schedule":
        # Running via external scheduler (Railway, Render, cron) — always send
        skip_check = True

    if not skip_check:
        if not _is_tehran_send_window():
            tehran = pytz.timezone("Asia/Tehran")
            now = datetime.now(tehran)
            print(f"Outside send window (Tehran: {now.strftime('%H:%M')}). Skipping.")
            sys.exit(0)

    run_digest()


if __name__ == "__main__":
    main()
