import os
from datetime import date, datetime

import requests

_SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
_SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_TABLE = "ai_news"


def save_digest(articles: list[dict], digest_date: date | None = None) -> list[dict]:
    """Persist processed articles to Supabase and return rows with ids."""
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        print("Supabase credentials missing; skipping database save.")
        return articles

    if digest_date is None:
        digest_date = date.today()

    headers = {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    rows = []
    for article in articles:
        row = {
            "title_fa": article["title_fa"],
            "summary_fa": article["summary_fa"],
            "title_en": article.get("title_en", ""),
            "source": article["source"],
            "url": article["url"],
            "published_at": article.get("published", datetime.utcnow().isoformat()),
            "importance_rank": article["importance_rank"],
            "image_url": article.get("image_url") or None,
            "video_url": article.get("video_url") or None,
            "digest_date": digest_date.isoformat(),
            "sent_to_telegram": False,
        }
        rows.append(row)

    resp = requests.post(
        f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
        headers=headers,
        json=rows,
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        print(f"Supabase insert error ({resp.status_code}): {resp.text[:300]}")
        return articles

    saved = resp.json()
    print(f"Saved {len(saved)} articles to Supabase (digest_date={digest_date})")
    return saved


def mark_sent(ids: list[int]) -> None:
    """Mark articles as sent to Telegram."""
    if not _SUPABASE_URL or not _SUPABASE_KEY or not ids:
        return

    headers = {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    id_filter = ",".join(str(i) for i in ids)
    requests.patch(
        f"{_SUPABASE_URL}/rest/v1/{_TABLE}?id=in.({id_filter})",
        headers=headers,
        json={"sent_to_telegram": True},
        timeout=30,
    )
