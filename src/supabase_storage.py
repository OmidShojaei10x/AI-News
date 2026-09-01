import os
from datetime import date, datetime

import requests

_SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
_SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_TABLE = "ai_news"


def save_digest(articles: list[dict], digest_date: date | None = None) -> list[dict]:
    """Persist processed articles to Supabase and return the saved rows."""
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        print("Supabase credentials missing; skipping database save.")
        return articles

    digest_date = digest_date or date.today()
    saved: list[dict] = []

    for article in articles:
        payload = {
            "title_fa": article["title_fa"],
            "summary_fa": article["summary_fa"],
            "title_en": article.get("title_en"),
            "source": article.get("source"),
            "url": article["url"],
            "published_at": article.get("published"),
            "importance_rank": article.get("importance_rank"),
            "image_url": article.get("image_url") or None,
            "video_url": article.get("video_url") or None,
            "sent_to_telegram": False,
            "digest_date": digest_date.isoformat(),
        }

        response = requests.post(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            headers={
                "apikey": _SUPABASE_KEY,
                "Authorization": f"Bearer {_SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json=payload,
            timeout=30,
        )

        if response.status_code in (200, 201):
            row = response.json()
            if isinstance(row, list) and row:
                article["supabase_id"] = row[0].get("id")
            saved.append(article)
            print(f"  Saved to Supabase: {article['title_fa'][:50]}...")
        else:
            print(
                f"  Supabase insert failed ({response.status_code}): "
                f"{response.text[:200]}"
            )
            saved.append(article)

    return saved


def mark_sent(article_ids: list[int]) -> None:
    """Mark articles as sent to Telegram."""
    if not _SUPABASE_URL or not _SUPABASE_KEY or not article_ids:
        return

    for article_id in article_ids:
        requests.patch(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}?id=eq.{article_id}",
            headers={
                "apikey": _SUPABASE_KEY,
                "Authorization": f"Bearer {_SUPABASE_KEY}",
                "Content-Type": "application/json",
            },
            json={"sent_to_telegram": True},
            timeout=30,
        )
