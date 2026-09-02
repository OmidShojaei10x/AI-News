import os
from datetime import date, datetime

import requests

_SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
_SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_TABLE = "ai_news"


def _headers() -> dict:
    return {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def save_digest(articles: list[dict], digest_date: date | None = None) -> list[dict]:
    """Persist processed articles to Supabase and return saved rows."""
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        print("Supabase credentials missing; skipping database save.")
        return []

    digest_date = digest_date or date.today()
    url = f"{_SUPABASE_URL.rstrip('/')}/rest/v1/{_TABLE}"
    saved: list[dict] = []

    for article in articles:
        payload = {
            "title_fa": article["title_fa"],
            "summary_fa": article["summary_fa"],
            "title_en": article.get("title_en", ""),
            "source": article.get("source", ""),
            "url": article["url"],
            "published_at": article.get("published"),
            "importance_rank": article.get("importance_rank"),
            "image_url": article.get("image_url") or None,
            "video_url": article.get("video_url") or None,
            "digest_date": digest_date.isoformat(),
            "sent_to_telegram": False,
        }

        response = requests.post(url, headers=_headers(), json=payload, timeout=30)
        if response.status_code >= 400:
            print(f"Supabase insert error: {response.status_code} {response.text[:200]}")
            continue

        rows = response.json()
        if rows:
            saved.append(rows[0])

    return saved


def mark_sent(article_ids: list[int]) -> None:
    """Mark articles as sent to Telegram."""
    if not _SUPABASE_URL or not _SUPABASE_KEY or not article_ids:
        return

    url = f"{_SUPABASE_URL.rstrip('/')}/rest/v1/{_TABLE}"
    params = {"id": f"in.({','.join(str(i) for i in article_ids)})"}
    requests.patch(
        url,
        headers=_headers(),
        params=params,
        json={"sent_to_telegram": True},
        timeout=30,
    )
