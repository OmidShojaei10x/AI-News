import json
import os
import re
import time

import requests

MODEL = "gemini-3.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
MAX_INPUT_ARTICLES = 50
MAX_OUTPUT_ARTICLES = 3


def process_news(articles: list[dict]) -> list[dict]:
    """Rank, deduplicate, translate and summarise articles in Persian via Gemini."""

    api_key = os.environ["GEMINI_API_KEY"]

    condensed = []
    for i, a in enumerate(articles[:MAX_INPUT_ARTICLES]):
        condensed.append(
            {
                "id": i,
                "title": a["title"],
                "description": (a["description"] or "")[:300],
                "source": a["source"],
                "published": a["published"],
                "has_image": bool(a.get("image_url")),
                "has_video": bool(a.get("video_url")),
            }
        )

    articles_json = json.dumps(condensed, ensure_ascii=False, indent=2)

    prompt = f"""تو یک روزنامه‌نگار متخصص در حوزه هوش مصنوعی هستی.
لیست زیر اخبار ۲۴ ساعت گذشته دنیای هوش مصنوعی است:

{articles_json}

وظایف:
۱. خبرهای تکراری یا خیلی مشابه را حذف کن (یکی نگه‌دار).
۲. حداکثر {MAX_OUTPUT_ARTICLES} خبر مهم را بر اساس تأثیرگذاری و جذابیت انتخاب کن.
۳. برای هر خبر:
   - عنوان را به فارسی روان و دقیق ترجمه کن.
   - یک خلاصه ۲ تا ۴ جمله‌ای به فارسی بنویس که اهمیت و جزئیات کلیدی را توضیح دهد.
   - مهم‌ترین خبر، importance_rank=1 داشته باشد.

فقط یک JSON خالص (بدون markdown، بدون توضیح اضافه) برگردان:
[
  {{
    "id": <شناسه اصلی>,
    "title_fa": "<عنوان فارسی>",
    "summary_fa": "<خلاصه فارسی>",
    "importance_rank": <عدد از ۱ به بالا>
  }}
]"""

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "تو یک روزنامه‌نگار متخصص هوش مصنوعی هستی که "
                        "اخبار را به فارسی روان ترجمه و خلاصه می‌کنی."
                    )
                }
            ]
        },
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 16384,
            "responseMimeType": "application/json",
        },
    }

    response = None
    for attempt in range(3):
        response = requests.post(
            API_URL,
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": api_key,
            },
            json=payload,
            timeout=120,
        )
        if response.status_code in (429, 500, 503):
            wait = 2 ** attempt
            print(f"Gemini API {response.status_code}; retrying in {wait}s...")
            time.sleep(wait)
            continue
        break

    if response is None:
        raise RuntimeError("Gemini API request failed")
    response.raise_for_status()

    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini returned no candidates: {data}")

    candidate = candidates[0]
    finish_reason = candidate.get("finishReason")
    if finish_reason == "MAX_TOKENS":
        raise RuntimeError("Gemini response was truncated (MAX_TOKENS)")

    raw = candidate["content"]["parts"][0]["text"].strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    processed: list[dict] = json.loads(raw)

    article_map = {i: a for i, a in enumerate(articles[:MAX_INPUT_ARTICLES])}
    result = []
    for item in sorted(processed, key=lambda x: x["importance_rank"]):
        orig = article_map.get(item["id"])
        if not orig:
            continue
        result.append(
            {
                "title_fa": item["title_fa"],
                "summary_fa": item["summary_fa"],
                "importance_rank": item["importance_rank"],
                "title_en": orig["title"],
                "source": orig["source"],
                "url": orig["url"],
                "published": orig["published"],
                "image_url": orig.get("image_url", ""),
                "video_url": orig.get("video_url", ""),
            }
        )

    return result
