import calendar
import time
from datetime import datetime, timezone, timedelta

import feedparser
import requests
from bs4 import BeautifulSoup

RSS_FEEDS = [
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "name": "TechCrunch"},
    {"url": "https://venturebeat.com/ai/feed/", "name": "VentureBeat"},
    {"url": "https://www.technologyreview.com/feed/", "name": "MIT Technology Review"},
    {"url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "name": "The Verge"},
    {"url": "https://www.wired.com/feed/tag/artificial-intelligence/rss", "name": "Wired"},
    {"url": "https://www.artificialintelligence-news.com/feed/", "name": "AI News"},
    {"url": "https://huggingface.co/blog/feed.xml", "name": "Hugging Face"},
    {"url": "https://blog.google/technology/ai/rss/", "name": "Google AI Blog"},
    {"url": "https://openai.com/blog/rss/", "name": "OpenAI Blog"},
    {"url": "https://deepmind.google/blog/rss.xml", "name": "DeepMind"},
    {"url": "https://thenewstack.io/category/machine-learning/feed/", "name": "The New Stack"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AINewsBot/1.0; "
        "+https://github.com/OmidShojaei10x/News-AI)"
    )
}


def _parse_date(entry) -> datetime:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.fromtimestamp(calendar.timegm(val), tz=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def _extract_image(entry) -> str:
    # media:content
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            url = m.get("url", "")
            if url:
                return url

    # media:thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get("url", "")
        if url:
            return url

    # enclosures
    for enc in getattr(entry, "enclosures", []):
        if "image" in enc.get("type", ""):
            url = enc.get("href") or enc.get("url", "")
            if url:
                return url

    # look inside HTML content / summary
    for field in ("content", "summary", "description"):
        html = ""
        if field == "content":
            content_list = getattr(entry, "content", None)
            if content_list:
                html = content_list[0].get("value", "")
        else:
            html = getattr(entry, field, "")

        if html:
            soup = BeautifulSoup(html, "html.parser")
            img = soup.find("img")
            if img:
                src = img.get("src") or img.get("data-src", "")
                if src and src.startswith("http"):
                    return src

    return ""


def _extract_video(entry) -> str:
    import re

    for enc in getattr(entry, "enclosures", []):
        if "video" in enc.get("type", ""):
            return enc.get("href") or enc.get("url", "")

    for field in ("content", "summary"):
        html = ""
        if field == "content":
            content_list = getattr(entry, "content", None)
            if content_list:
                html = content_list[0].get("value", "")
        else:
            html = getattr(entry, field, "")

        if html:
            m = re.search(r"https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+", html)
            if m:
                return m.group(0)
            m = re.search(r"https?://youtu\.be/[\w-]+", html)
            if m:
                return m.group(0)

    return ""


def _clean_description(entry) -> str:
    html = ""
    content_list = getattr(entry, "content", None)
    if content_list:
        html = content_list[0].get("value", "")
    if not html:
        html = getattr(entry, "summary", "") or getattr(entry, "description", "")

    if html:
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(soup.get_text(separator=" ", strip=True).split())
        return text[:600]

    return ""


def _fetch_feed(feed_info: dict) -> list[dict]:
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    try:
        feed = feedparser.parse(feed_info["url"], request_headers=HEADERS)
        for entry in feed.entries:
            pub_date = _parse_date(entry)
            if pub_date < cutoff:
                continue
            title = (entry.get("title") or "").strip()
            url = (entry.get("link") or "").strip()
            if not title or not url:
                continue
            articles.append(
                {
                    "title": title,
                    "description": _clean_description(entry),
                    "url": url,
                    "source": feed_info["name"],
                    "published": pub_date.isoformat(),
                    "image_url": _extract_image(entry),
                    "video_url": _extract_video(entry),
                }
            )
    except Exception as exc:
        print(f"    [{feed_info['name']}] error: {type(exc).__name__}: {exc}")

    return articles


def _fetch_og_image(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for prop in ("og:image", "twitter:image"):
            tag = soup.find("meta", property=prop) or soup.find(
                "meta", attrs={"name": prop}
            )
            if tag and tag.get("content", "").startswith("http"):
                return tag["content"]
    except Exception as exc:
        print(f"    OG image fetch failed for {url[:60]}: {exc}")
    return ""


def enrich_images(articles: list[dict]) -> list[dict]:
    """Fill missing image_url from page Open Graph tags."""
    for article in articles:
        if not article.get("image_url"):
            img = _fetch_og_image(article["url"])
            if img:
                article["image_url"] = img
            time.sleep(0.3)
    return articles


def fetch_all_news() -> list[dict]:
    all_articles: list[dict] = []

    for feed_info in RSS_FEEDS:
        print(f"  Fetching {feed_info['name']}...")
        articles = _fetch_feed(feed_info)
        print(f"    → {len(articles)} articles")
        all_articles.extend(articles)
        time.sleep(0.4)

    # deduplicate by URL
    seen: set[str] = set()
    unique = []
    for a in all_articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    # newest first
    unique.sort(key=lambda x: x["published"], reverse=True)
    return enrich_images(unique)
