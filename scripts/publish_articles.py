#!/usr/bin/env python3
"""Publish prepared Persian articles to Telegram and Supabase."""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests

from scripts._config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from scripts._supabase import insert_news, log_check


def _send_photo(caption: str, photo_url: str) -> bool:
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    resp = requests.post(
        api,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "photo": photo_url,
            "caption": caption[:1024],
            "parse_mode": "HTML",
        },
        timeout=30,
    )
    result = resp.json()
    if not result.get("ok"):
        print(f"Photo send failed: {result.get('description')}", file=sys.stderr)
        return False
    return True


def _send_message(text: str) -> bool:
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(
        api,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text[:4096],
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=30,
    )
    result = resp.json()
    if not result.get("ok"):
        print(f"Message send failed: {result.get('description')}", file=sys.stderr)
        return False
    return True


def _format_caption(article: dict) -> str:
    lines = [
        f"🤖 <b>{article['title_fa']}</b>",
        "",
        article["summary_fa"],
        "",
        f"📰 <b>منبع:</b> {article.get('source', '')}",
        f'🔗 <a href="{article["url"]}">مطالعه کامل خبر</a>',
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON file with articles to publish")
    parser.add_argument("--slot", required=True)
    parser.add_argument("--lookback", type=int, required=True)
    parser.add_argument("--found", type=int, required=True)
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    articles = data if isinstance(data, list) else data.get("articles", [])
    sent = 0

    for article in articles:
        caption = _format_caption(article)
        ok = False
        if article.get("image_url"):
            ok = _send_photo(caption, article["image_url"])
        if not ok:
            ok = _send_message(caption)
        if ok:
            article["check_slot"] = args.slot
            insert_news(article)
            sent += 1
            print(f"Sent: {article['title_fa']}", file=sys.stderr)
        time.sleep(1.5)

    log_check(args.slot, args.lookback, args.found, sent)
    print(json.dumps({"sent": sent, "found": args.found, "slot": args.slot}))


if __name__ == "__main__":
    main()
