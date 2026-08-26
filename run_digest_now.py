#!/usr/bin/env python3
"""One-shot digest runner with manual Persian summaries when Gemini is unavailable."""

import json
import os
import sys
from datetime import date, datetime, timezone

import requests

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.news_fetcher import enrich_images, fetch_all_news
from src.supabase_storage import save_articles
from src.telegram_sender import send_daily_digest

TOP_3_MANUAL = [
    {
        "match": "bill gates",
        "title_fa": "بیل گیتس: هوش مصنوعی از مرزهای خطر عبور کرده است",
        "summary_fa": (
            "بیل گیتس در یادداشتی جدید هشدار داد که AI از چند آستانه خطر — "
            "بیوتکنولوژی، سایبری، اختلال در بازار کار و وابستگی روانی-اجتماعی — "
            "عبور کرده و حفاظت‌ها عقب مانده‌اند. او پیشنهاد داد مشاغل «اختصاصی انسان» "
            "تعریف شود و حتی مالیات روی ربات‌ها برای حمایت از نیروی کار بررسی گردد."
        ),
        "fallback_url": "https://www.technologyreview.com/2026/08/26/1142946/bill-gates-ai-danger-threshold/",
        "fallback_source": "MIT Technology Review",
        "image_url": "https://wp.technologyreview.com/wp-content/uploads/2026/08/MIT_07_21_2026_0057.jpg",
        "importance_rank": 1,
    },
    {
        "match": "jalapeno",
        "title_fa": "اوپن‌ای‌آی تراشه استنتاج اختصاصی «Jalapeño» را معرفی کرد",
        "summary_fa": (
            "سام آلتمن از اولین نتایج تراشه سفارشی Jalapeño خبر داد؛ "
            "طبق OpenAI این چیپ ۱.۵ تا ۴.۱ برابر کارایی بیشتر به‌ازای هر وات "
            "و تأخیر کمتر نسبت به سیستم‌های مقایسه‌ای دارد. "
            "استقرار در زیرساخت OpenAI تا پایان سال برنامه‌ریزی شده است."
        ),
        "fallback_url": "https://techcrunch.com/2026/08/25/openais-jalapeno-chip-is-built-for-fast-inference-at-scale-benchmarks-show/",
        "fallback_source": "TechCrunch / OpenAI",
        "image_url": "https://techcrunch.com/wp-content/uploads/2026/08/Jalapeno-chip-final.jpeg?resize=1200,900",
        "importance_rank": 2,
    },
    {
        "match": "reddit",
        "title_fa": "سقوط ۸۶٪ استناد ChatGPT به Reddit پس از تغییر جستجوی OpenAI",
        "summary_fa": (
            "داده‌های Promptwatch نشان می‌دهد سهم reddit.com در استنادهای ChatGPT Search "
            "در سه روز از ۳.۸۳٪ به ۰.۵۲٪ رسید — پس از تغییر ناگهانی ۸ اوت که "
            "اپراتور site: در جستجوها گسترش یافت. سهم از دست‌رفته عمدتاً به "
            "مستندات vendor منتقل شد، نه فروم‌های دیگر."
        ),
        "fallback_url": "https://aitoolsrecap.com/Blog/ai-news-august-26-2026",
        "fallback_source": "AIToolsRecap / Promptwatch",
        "image_url": "https://aitoolsrecap.com/ArticleImages/default_article.jpg",
        "importance_rank": 3,
    },
]


def _find_article(articles: list[dict], keyword: str) -> dict | None:
    kw = keyword.lower()
    for a in articles:
        if kw in a["title"].lower() or kw in a.get("description", "").lower():
            return a
        if kw in a["url"].lower():
            return a
    return None


def build_top3(articles: list[dict]) -> list[dict]:
    result = []
    for spec in TOP_3_MANUAL:
        orig = _find_article(articles, spec["match"])
        item = {
            "title_fa": spec["title_fa"],
            "summary_fa": spec["summary_fa"],
            "importance_rank": spec["importance_rank"],
            "title_en": orig["title"] if orig else spec["title_fa"],
            "source": spec["fallback_source"],
            "url": spec["fallback_url"],
            "published": orig["published"] if orig else datetime.now(timezone.utc).isoformat(),
            "image_url": spec.get("image_url", ""),
            "video_url": (orig or {}).get("video_url", ""),
        }
        result.append(item)

    return result


def try_gemini(articles: list[dict]) -> list[dict] | None:
    if not os.environ.get("GEMINI_API_KEY"):
        return None
    try:
        from src.news_processor import process_news

        return process_news(articles)[:3]
    except Exception as exc:
        print(f"Gemini processing failed: {exc}")
        return None


def main() -> None:
    print("── Fetching AI news ──")
    articles = fetch_all_news()
    print(f"Found {len(articles)} articles")

    processed = try_gemini(articles)
    if not processed:
        print("Using curated top-3 summaries")
        processed = build_top3(articles)

    print(json.dumps(
        [{"rank": a["importance_rank"], "title": a["title_fa"]} for a in processed],
        ensure_ascii=False,
        indent=2,
    ))

    print("\n── Saving to Supabase ──")
    save_articles(processed, digest_date=date.today())

    print("\n── Sending to Telegram ──")
    send_daily_digest(processed)
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
