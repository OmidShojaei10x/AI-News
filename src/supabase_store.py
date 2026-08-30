import os
from datetime import date, datetime

import pytz
import requests

_SUPABASE_URL = os.environ.get(
    "SUPABASE_URL", "https://uwpkiioexphefbiddmmf.supabase.co"
)
_SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_TABLE = "ai_news"
_HEADERS = {
    "apikey": _SUPABASE_KEY,
    "Authorization": f"Bearer {_SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def _today_tehran() -> date:
    tehran = pytz.timezone("Asia/Tehran")
    return datetime.now(tehran).date()


def _row_from_article(article: dict, digest_date: date) -> dict:
    return {
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


def save_articles(articles: list[dict], digest_date: date | None = None) -> list[dict]:
    """Upsert today's digest articles into Supabase (by url)."""
    if not _SUPABASE_KEY:
        print("SUPABASE_ANON_KEY not set; skipping database save.")
        return articles

    digest_date = digest_date or _today_tehran()
    saved: list[dict] = []

    for article in articles:
        row = _row_from_article(article, digest_date)
        url = row["url"]

        existing = requests.get(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            headers={**_HEADERS, "Prefer": "return=representation"},
            params={
                "url": f"eq.{url}",
                "digest_date": f"eq.{digest_date.isoformat()}",
                "select": "id",
            },
            timeout=30,
        )
        existing.raise_for_status()

        if existing.json():
            resp = requests.patch(
                f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                headers=_HEADERS,
                params={
                    "url": f"eq.{url}",
                    "digest_date": f"eq.{digest_date.isoformat()}",
                },
                json=row,
                timeout=30,
            )
        else:
            resp = requests.post(
                f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                headers=_HEADERS,
                json=row,
                timeout=30,
            )

        resp.raise_for_status()
        data = resp.json()
        if data:
            article["supabase_id"] = data[0]["id"]
        saved.append(article)

    return saved


def mark_sent(articles: list[dict]) -> None:
    """Mark articles as sent to Telegram."""
    if not _SUPABASE_KEY:
        return

    for article in articles:
        article_id = article.get("supabase_id")
        if not article_id:
            continue
        requests.patch(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            headers={**_HEADERS, "Prefer": "return=minimal"},
            params={"id": f"eq.{article_id}"},
            json={"sent_to_telegram": True},
            timeout=30,
        )


def get_todays_digest(limit: int = 3) -> list[dict]:
    """Load today's digest from Supabase, ordered by importance."""
    if not _SUPABASE_KEY:
        return []

    digest_date = _today_tehran()
    resp = requests.get(
        f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
        headers={**_HEADERS, "Prefer": "return=representation"},
        params={
            "digest_date": f"eq.{digest_date.isoformat()}",
            "order": "importance_rank.asc",
            "limit": str(limit),
            "select": "*",
        },
        timeout=30,
    )
    resp.raise_for_status()
    rows = resp.json()

    articles = []
    for row in rows:
        articles.append(
            {
                "title_fa": row["title_fa"],
                "summary_fa": row["summary_fa"],
                "title_en": row.get("title_en", ""),
                "source": row.get("source", ""),
                "url": row["url"],
                "published": row.get("published_at"),
                "importance_rank": row.get("importance_rank"),
                "image_url": row.get("image_url") or "",
                "video_url": row.get("video_url") or "",
                "supabase_id": row["id"],
            }
        )
    return articles
