import os
import time

import requests

from src.rtl_text import fix_rtl

_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
# Channel: اخبار هوش مصنوعی — https://t.me/+JPVZfc1WuRQ3NGRk
_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1004366053988")
_API = f"https://api.telegram.org/bot{_BOT_TOKEN}"

_SLOT_LABELS = {
    "morning": "صبح (۹:۰۰)",
    "noon": "ظهر (۱۲:۰۰)",
    "evening": "شب (۲۱:۰۰)",
}


def _api(method: str, data: dict, retries: int = 3) -> dict:
    url = f"{_API}/{method}"
    delay = 2
    for attempt in range(retries):
        try:
            r = requests.post(url, json=data, timeout=30)
            result = r.json()
            if result.get("ok"):
                return result
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


def _format_article(article: dict) -> str:
    title = fix_rtl(article["title_fa"])
    summary = fix_rtl(article["summary_fa"])
    source = fix_rtl(article.get("source", ""))

    lines = [
        f"🔔 <b>{title}</b>",
        "",
        summary,
        "",
        f"📰 <b>{fix_rtl('منبع:')}</b> {source}",
    ]

    if article.get("video_url"):
        lines.append(
            f'🎬 <b>{fix_rtl("ویدیو:")}</b> '
            f'<a href="{article["video_url"]}">{fix_rtl("مشاهده ویدیو")}</a>'
        )

    lines.append(
        f'🔗 <a href="{article["url"]}">{fix_rtl("مطالعه کامل خبر")}</a>'
    )
    return "\n".join(lines)


def send_article(article: dict) -> bool:
    """Send a single article to Telegram. Returns True on success."""
    text = _format_article(article)
    sent = False

    if article.get("image_url"):
        result = _send_photo(article["image_url"], text)
        sent = result.get("ok", False)

    if not sent:
        result = _send_message(text)
        sent = result.get("ok", False)

    return sent


def send_alerts(articles: list[dict], check_slot: str) -> None:
    """Send each important article as a separate Telegram message."""
    if not articles:
        return

    slot_label = _SLOT_LABELS.get(check_slot, check_slot)
    sent_count = 0
    for article in articles:
        if send_article(article):
            sent_count += 1
        time.sleep(1.5)

    print(f"Sent {sent_count} alert(s) to Telegram (slot={slot_label})")
