import os
from datetime import datetime

import pytz
import requests

_SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
_SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_NEWS_TABLE = "ai_news"
_CHECKS_TABLE = "ai_news_checks"
_MAX_PER_CHECK = 3


def _headers() -> dict:
    return {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _configured() -> bool:
    return bool(_SUPABASE_URL and _SUPABASE_KEY)


def get_sent_urls() -> set[str]:
    """Return URLs already sent to Telegram."""
    if not _configured():
        print("Supabase credentials missing; skipping dedup lookup.")
        return set()

    response = requests.get(
        f"{_SUPABASE_URL}/rest/v1/{_NEWS_TABLE}",
        headers=_headers(),
        params={
            "select": "url",
            "sent_to_telegram": "eq.true",
        },
        timeout=30,
    )
    response.raise_for_status()
    return {row["url"] for row in response.json()}


def save_articles(articles: list[dict], check_slot: str) -> list[dict]:
    """Persist important articles to Supabase."""
    if not _configured():
        print("Supabase credentials missing; skipping database save.")
        return []

    tehran = pytz.timezone("Asia/Tehran")
    digest_date = datetime.now(tehran).date().isoformat()
    top = articles[:_MAX_PER_CHECK]

    rows = []
    for article in top:
        published = article.get("published")
        published_at = None
        if published:
            try:
                published_at = datetime.fromisoformat(
                    published.replace("Z", "+00:00")
                ).isoformat()
            except ValueError:
                published_at = published

        rows.append(
            {
                "title_fa": article["title_fa"],
                "summary_fa": article["summary_fa"],
                "title_en": article.get("title_en", ""),
                "source": article.get("source", ""),
                "url": article["url"],
                "published_at": published_at,
                "importance_rank": article.get("importance_rank"),
                "image_url": article.get("image_url") or None,
                "video_url": article.get("video_url") or None,
                "digest_date": digest_date,
                "check_slot": check_slot,
                "sent_to_telegram": False,
            }
        )

    if not rows:
        return []

    response = requests.post(
        f"{_SUPABASE_URL}/rest/v1/{_NEWS_TABLE}",
        headers={**_headers(), "Prefer": "resolution=ignore-duplicates,return=representation"},
        json=rows,
        timeout=30,
    )
    response.raise_for_status()
    saved = response.json()
    print(f"Saved {len(saved)} articles to Supabase (slot={check_slot})")
    return saved


def log_check(
    check_slot: str,
    lookback_hours: int,
    articles_found: int,
    articles_sent: int,
) -> None:
    """Log every check run, including when no news is sent."""
    if not _configured():
        print("Supabase credentials missing; skipping check log.")
        return

    response = requests.post(
        f"{_SUPABASE_URL}/rest/v1/{_CHECKS_TABLE}",
        headers=_headers(),
        json={
            "check_slot": check_slot,
            "lookback_hours": lookback_hours,
            "articles_found": articles_found,
            "articles_sent": articles_sent,
        },
        timeout=30,
    )
    response.raise_for_status()
    print(
        f"Logged check: slot={check_slot}, found={articles_found}, sent={articles_sent}"
    )


def mark_sent(urls: list[str]) -> None:
    """Mark articles as sent to Telegram."""
    if not _configured() or not urls:
        return

    for url in urls:
        requests.patch(
            f"{_SUPABASE_URL}/rest/v1/{_NEWS_TABLE}",
            headers=_headers(),
            params={"url": f"eq.{url}"},
            json={"sent_to_telegram": True},
            timeout=30,
        ).raise_for_status()
