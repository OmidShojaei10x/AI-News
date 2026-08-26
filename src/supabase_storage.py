import os
from datetime import date, datetime

import requests

_SUPABASE_URL = os.environ.get(
    "SUPABASE_URL", "https://uwpkiioexphefbiddmmf.supabase.co"
)
_SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

_HEADERS = {
    "apikey": _SUPABASE_KEY,
    "Authorization": f"Bearer {_SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def save_articles(articles: list[dict], digest_date: date | None = None) -> list[dict]:
    """Persist processed articles to Supabase and mark them as sent."""
    if not _SUPABASE_KEY:
        print("SUPABASE_ANON_KEY not set — skipping database save")
        return []

    digest_date = digest_date or date.today()
    rows = []
    for article in articles:
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
                "importance_rank": article.get("importance_rank", 0),
                "image_url": article.get("image_url", ""),
                "video_url": article.get("video_url", ""),
                "sent_to_telegram": True,
                "digest_date": digest_date.isoformat(),
            }
        )

    # Remove any existing rows with the same URLs (unique constraint)
    for row in rows:
        delete_url = f"{_SUPABASE_URL}/rest/v1/ai_news?url=eq.{requests.utils.quote(row['url'], safe='')}"
        requests.delete(delete_url, headers=_HEADERS, timeout=30)

    # Also clear today's digest rows
    delete_url = (
        f"{_SUPABASE_URL}/rest/v1/ai_news"
        f"?digest_date=eq.{digest_date.isoformat()}"
    )
    requests.delete(delete_url, headers=_HEADERS, timeout=30)

    insert_headers = {**_HEADERS, "Prefer": "return=representation,resolution=merge-duplicates"}
    insert_url = f"{_SUPABASE_URL}/rest/v1/ai_news?on_conflict=url"
    response = requests.post(insert_url, headers=insert_headers, json=rows, timeout=30)
    if response.status_code == 409:
        # Fallback: upsert via PATCH per row
        saved = []
        for row in rows:
            patch_url = (
                f"{_SUPABASE_URL}/rest/v1/ai_news"
                f"?url=eq.{requests.utils.quote(row['url'], safe='')}"
            )
            upsert_headers = {**_HEADERS, "Prefer": "return=representation"}
            pr = requests.patch(patch_url, headers=upsert_headers, json=row, timeout=30)
            if pr.status_code == 200 and pr.json():
                saved.extend(pr.json())
            else:
                ir = requests.post(
                    f"{_SUPABASE_URL}/rest/v1/ai_news",
                    headers=_HEADERS,
                    json=row,
                    timeout=30,
                )
                ir.raise_for_status()
                saved.extend(ir.json())
        print(f"Saved {len(saved)} articles to Supabase (upsert)")
        return saved

    response.raise_for_status()
    saved = response.json()
    print(f"Saved {len(saved)} articles to Supabase")
    return saved
