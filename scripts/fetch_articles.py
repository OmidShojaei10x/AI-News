#!/usr/bin/env python3
"""Fetch recent AI news articles, excluding URLs already in Supabase."""

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calendar
import time

import feedparser
import requests
from bs4 import BeautifulSoup

from scripts._config import current_slot
from scripts._supabase import get_sent_urls

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
    "User-Agent": "Mozilla/5.0 (compatible; AINewsBot/1.0; +https://github.com/OmidShojaei10x/AI-News)"
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
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            url = m.get("url", "")
            if url:
                return url
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get("url", "")
        if url:
            return url
    for enc in getattr(entry, "enclosures", []):
        if "image" in enc.get("type", ""):
            url = enc.get("href") or enc.get("url", "")
            if url:
                return url
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


def fetch_feed(feed_info: dict, cutoff: datetime) -> list[dict]:
    articles = []
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
                }
            )
    except Exception as exc:
        print(f"  [{feed_info['name']}] error: {exc}", file=sys.stderr)
    return articles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lookback", type=int, help="Lookback hours (default: auto from slot)")
    parser.add_argument("--output", default="/tmp/fetched_articles.json")
    args = parser.parse_args()

    slot, default_lookback = current_slot()
    lookback = args.lookback or default_lookback
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback)

    print(f"Slot: {slot}, lookback: {lookback}h", file=sys.stderr)

    known_urls = get_sent_urls()
    print(f"Known URLs in DB: {len(known_urls)}", file=sys.stderr)

    all_articles: list[dict] = []
    for feed_info in RSS_FEEDS:
        print(f"  Fetching {feed_info['name']}...", file=sys.stderr)
        articles = fetch_feed(feed_info, cutoff)
        print(f"    → {len(articles)} recent", file=sys.stderr)
        all_articles.extend(articles)
        time.sleep(0.3)

    seen: set[str] = set()
    unique = []
    for a in all_articles:
        if a["url"] in seen or a["url"] in known_urls:
            continue
        seen.add(a["url"])
        unique.append(a)

    unique.sort(key=lambda x: x["published"], reverse=True)

    meta = {"slot": slot, "lookback_hours": lookback, "count": len(unique)}
    output = {"meta": meta, "articles": unique}

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(json.dumps(meta, ensure_ascii=False))
    print(f"Saved {len(unique)} new articles to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
