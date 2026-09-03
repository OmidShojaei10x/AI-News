import os
import sys
from datetime import datetime

import pytz

SLOT_WINDOWS = {
    "morning": (8 * 60 + 45, 9 * 60 + 30, 24),
    "noon": (11 * 60 + 45, 12 * 60 + 30, 8),
    "evening": (20 * 60 + 45, 21 * 60 + 30, 8),
}


def detect_check_slot() -> tuple[str, int]:
    """Return (check_slot, lookback_hours) based on Tehran time."""
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

    # Fallback for manual runs outside scheduled windows
    if minutes < 11 * 60 + 45:
        return "morning", 24
    if minutes < 20 * 60 + 45:
        return "noon", 8
    return "evening", 8


def _in_send_window() -> bool:
    tehran = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran)
    minutes = now.hour * 60 + now.minute

    for _, (start, end, _) in SLOT_WINDOWS.items():
        if start <= minutes <= end:
            return True
    return False


def run_check() -> None:
    """Fetch, filter, and optionally alert on important AI news."""
    from src.news_fetcher import enrich_images, fetch_all_news
    from src.news_processor import process_news
    from src.supabase_storage import get_sent_urls, log_check, mark_sent, save_articles
    from src.telegram_sender import send_alerts

    check_slot, lookback_hours = detect_check_slot()
    print(f"── Check slot: {check_slot} | lookback: {lookback_hours}h ──")

    print(f"\n── Step 1: Fetching AI news (last {lookback_hours}h) ──")
    articles = fetch_all_news(lookback_hours=lookback_hours)
    print(f"Total unique articles: {len(articles)}")

    sent_urls = get_sent_urls()
    if sent_urls:
        before = len(articles)
        articles = [a for a in articles if a["url"] not in sent_urls]
        print(f"After dedup: {len(articles)} (removed {before - len(articles)} already sent)")

    if not articles:
        print("No new articles. Logging check.")
        log_check(check_slot, lookback_hours, articles_found=0, articles_sent=0)
        return

    print("\n── Step 2: Filtering importance & translating with Gemini ──")
    important = process_news(articles)
    print(f"Important articles: {len(important)}")

    if important:
        important = enrich_images(important)

    if not important:
        print("No important news. Logging check (no Telegram).")
        log_check(check_slot, lookback_hours, articles_found=len(articles), articles_sent=0)
        return

    print("\n── Step 3: Saving to Supabase ──")
    save_articles(important, check_slot=check_slot)

    print("\n── Step 4: Sending alerts to Telegram ──")
    send_alerts(important, check_slot=check_slot)
    mark_sent([a["url"] for a in important])

    log_check(
        check_slot,
        lookback_hours,
        articles_found=len(articles),
        articles_sent=len(important),
    )
    print(f"\n✓ Sent {len(important)} alert(s) successfully!")


def main() -> None:
    force = os.environ.get("FORCE_SEND", "false").lower() == "true"
    github_event = os.environ.get("GITHUB_EVENT_NAME", "")

    skip_check = force or github_event == "workflow_dispatch"
    if not skip_check and github_event != "schedule":
        skip_check = True

    if not skip_check and not _in_send_window():
        tehran = pytz.timezone("Asia/Tehran")
        now = datetime.now(tehran)
        print(f"Outside send window (Tehran: {now.strftime('%H:%M')}). Skipping.")
        sys.exit(0)

    run_check()


if __name__ == "__main__":
    main()
