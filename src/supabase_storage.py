import os
from datetime import datetime

import pytz
import requests

_SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
_SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_TABLE = "ai_news"
_TOP_N = 3


def _headers() -> dict:
    return {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def save_digest(articles: list[dict]) -> list[dict]:
    """Persist the top-N digest articles to Supabase and return saved rows."""
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        print("Supabase credentials missing; skipping database save.")
        return []

    tehran = pytz.timezone("Asia/Tehran")
    digest_date = datetime.now(tehran).date().isoformat()
    top = articles[:_TOP_N]

    rows = []
    for article in top:
        published = article.get("published")
        published_at = None
        if published:
            try:
                published_at = datetime.fromisoformat(published.replace("Z", "+00:00")).isoformat()
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
                "sent_to_telegram": False,
            }
        )

    response = requests.post(
        f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
        headers=_headers(),
        json=rows,
        timeout=30,
    )
    response.raise_for_status()
    saved = response.json()
    print(f"Saved {len(saved)} articles to Supabase (digest_date={digest_date})")
    return saved


def mark_sent(urls: list[str]) -> None:
    """Mark articles as sent to Telegram."""
    if not _SUPABASE_URL or not _SUPABASE_KEY or not urls:
        return

    for url in urls:
        requests.patch(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            headers=_headers(),
            params={"url": f"eq.{url}"},
            json={"sent_to_telegram": True},
            timeout=30,
        ).raise_for_status()
