import requests

from scripts._config import SUPABASE_ANON_KEY, SUPABASE_URL


def _headers() -> dict:
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def get_sent_urls() -> set[str]:
    """Return URLs already stored in ai_news (sent or not)."""
    url = f"{SUPABASE_URL}/rest/v1/ai_news?select=url"
    resp = requests.get(url, headers=_headers(), timeout=30)
    resp.raise_for_status()
    return {row["url"] for row in resp.json()}


def insert_news(article: dict) -> None:
    payload = {
        "title_fa": article["title_fa"],
        "summary_fa": article["summary_fa"],
        "title_en": article.get("title_en"),
        "source": article.get("source"),
        "url": article["url"],
        "published_at": article.get("published"),
        "importance_rank": article.get("importance_rank", 1),
        "sent_to_telegram": True,
        "image_url": article.get("image_url"),
        "video_url": article.get("video_url"),
        "check_slot": article.get("check_slot"),
    }
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/ai_news",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()


def log_check(slot: str, lookback_hours: int, found: int, sent: int) -> None:
    payload = {
        "check_slot": slot,
        "lookback_hours": lookback_hours,
        "articles_found": found,
        "articles_sent": sent,
    }
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/ai_news_checks",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
