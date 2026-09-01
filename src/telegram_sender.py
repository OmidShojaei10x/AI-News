import os
import time
from datetime import datetime

import pytz
import requests

_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
_API = f"https://api.telegram.org/bot{_BOT_TOKEN}"

_RANK_EMOJIS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
_WEEKDAYS_FA = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"]


def _api(method: str, data: dict, retries: int = 3) -> dict:
    url = f"{_API}/{method}"
    delay = 2
    for attempt in range(retries):
        try:
            r = requests.post(url, json=data, timeout=30)
            result = r.json()
            if result.get("ok"):
                return result
            # Rate limit
            if result.get("error_code") == 429:
                wait = result.get("parameters", {}).get("retry_after", delay)
                print(f"Rate limited; waiting {wait}s")
                time.sleep(wait)
                continue
            print(f"Telegram error [{method}]: {result.get('description')}")
            return result
        except Exception as exc:
            print(f"Request error (attempt {attempt + 1}/{retries}): {exc}")
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
    return {}


def _send_message(text: str) -> dict:
    return _api(
        "sendMessage",
        {
            "chat_id": _CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
    )


def _send_photo(photo_url: str, caption: str) -> dict:
    return _api(
        "sendPhoto",
        {
            "chat_id": _CHAT_ID,
            "photo": photo_url,
            "caption": caption[:1024],
            "parse_mode": "HTML",
        },
    )


def _format_article(article: dict, index: int) -> str:
    emoji = _RANK_EMOJIS[index] if index < len(_RANK_EMOJIS) else f"{index + 1}."

    lines = [
        f"{emoji} <b>{article['title_fa']}</b>",
        "",
        article["summary_fa"],
        "",
        f"📰 <b>منبع:</b> {article['source']}",
    ]

    if article.get("video_url"):
        lines.append(
            f'🎬 <b>ویدیو:</b> <a href="{article["video_url"]}">مشاهده ویدیو</a>'
        )

    lines.append(f'🔗 <a href="{article["url"]}">مطالعه کامل خبر</a>')
    return "\n".join(lines)


def send_daily_digest(articles: list[dict]) -> None:
    tehran = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran)
    day_name = _WEEKDAYS_FA[now.weekday()]
    date_str = now.strftime("%Y/%m/%d")

    header = (
        "📡 <b>خبرنامه روزانه هوش مصنوعی</b>\n"
        f"📅 {day_name} — {date_str}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 <b>{len(articles)} خبر مهم</b> از ۲۴ ساعت گذشته در دنیای هوش مصنوعی"
    )
    _send_message(header)
    time.sleep(1)

    for i, article in enumerate(articles):
        text = _format_article(article, i)
        sent = False

        if article.get("image_url"):
            result = _send_photo(article["image_url"], text)
            sent = result.get("ok", False)

        if not sent:
            _send_message(text)

        time.sleep(1.5)

    footer = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔄 این خبرنامه هر روز ساعت ۸ صبح به‌طور خودکار ارسال می‌شود\n"
        "⚡️ <i>پردازش شده با هوش مصنوعی</i>"
    )
    _send_message(footer)

    from src.supabase_storage import mark_sent

    sent_ids = [a["supabase_id"] for a in articles if a.get("supabase_id")]
    if sent_ids:
        mark_sent(sent_ids)
