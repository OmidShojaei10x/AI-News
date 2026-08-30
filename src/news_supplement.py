"""Curated high-impact AI stories when RSS feeds return fewer than 3 items."""

from datetime import datetime, timezone

SUPPLEMENT_URLS = [
    {
        "url": "https://www.engadget.com/2246969/openai-pull-its-models-from-cursor-due-to-spacexai-acquisition/",
        "source": "Engadget",
        "title_fa": "اوپن‌ای‌آی مدل‌های خود را از Cursor قطع می‌کند",
        "summary_fa": (
            "پس از خرید Cursor توسط SpaceX، اوپن‌ای‌آی اعلام کرد تا ۱۲ نوامبر ۲۰۲۶ "
            "دسترسی این ابزار کدنویسی به مدل‌های GPT را قطع می‌کند. شرکت می‌گوید "
            "نمی‌تواند مطمئن باشد فناوری‌اش طبق شرایط استفاده به‌کار گرفته می‌شود. "
            "آنتروپیک در مقابل وعده افزایش ظرفیت Claude در Cursor را داده است."
        ),
    },
    {
        "url": "https://www.theguardian.com/technology/2026/aug/29/sharp-rise-in-incidents-of-ai-escaping-users-control-research-finds",
        "source": "The Guardian",
        "title_fa": "افزایش چشمگیر موارد فرار هوش مصنوعی از کنترل کاربران",
        "summary_fa": (
            "تحقیق Loss of Control Observatory نشان می‌دهد گزارش‌های واقعی از رفتار "
            "ناسازگار مدل‌ها در ژوئیه تقریباً دو برابر شده و بیش از ۳۰۰ مورد ثبت شده است. "
            "موارد شامل دروغ گفتن، دور زدن محدودیت‌ها و همکاری مخفیانه عامل‌های خودمختار است. "
            "کارشناسان خواستار گزارش‌دهی شفاف‌تر شرکت‌های هوش مصنوعی شده‌اند."
        ),
    },
]


PERSIAN_OVERRIDES = {
    "https://techcrunch.com/2026/08/29/sony-music-warner-sue-anthropic-alleging-a-brazen-campaign-of-intellectual-property-theft/": {
        "title_fa": "سونی و وارنر علیه آنتروپیک شکایت کردند",
        "summary_fa": (
            "ناشران موسیقی سونی و وارنر چاپل به همراه چندین ناشر دیگر آنتروپیک و "
            "بنیان‌گذارانش را به دزدی گسترده آثار دارای حق نسخه‌برداری متهم کرده‌اند. "
            "در شکایت ۴۸ صفحه‌ای ادعا شده شرکت با تورنت، اسکرپ و دانلود غیرقانونی "
            "هزاران آهنگ و متن آهنگ، مدل Claude را آموزش داده است. آنتروپیک "
            "این ادعاها را رد کرده و گفته در دادگاه از خود دفاع خواهد کرد."
        ),
    },
}


def apply_persian_overrides(articles: list[dict]) -> list[dict]:
    for article in articles:
        override = PERSIAN_OVERRIDES.get(article["url"])
        if override:
            article.update(override)
    return articles


def enrich_images(articles: list[dict]) -> list[dict]:
    """Fetch og:image for articles missing cover art."""
    import requests
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; AINewsBot/1.0; "
            "+https://github.com/OmidShojaei10x/AI-News)"
        )
    }
    for article in articles:
        if article.get("image_url"):
            continue
        try:
            resp = requests.get(article["url"], headers=headers, timeout=20)
            soup = BeautifulSoup(resp.text, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                article["image_url"] = og_image["content"]
        except Exception as exc:
            print(f"  [image] failed for {article['url']}: {exc}")
    return articles


def supplement_articles(articles: list[dict], target: int = 3) -> list[dict]:
    """Add curated stories missing from RSS results."""
    if len(articles) >= target:
        return articles

    import requests
    from bs4 import BeautifulSoup

    existing_urls = {a["url"] for a in articles}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; AINewsBot/1.0; "
            "+https://github.com/OmidShojaei10x/AI-News)"
        )
    }

    for item in SUPPLEMENT_URLS:
        if item["url"] in existing_urls:
            continue

        title_en = item.get("title_en", "")
        description = ""
        image_url = ""

        try:
            resp = requests.get(item["url"], headers=headers, timeout=20)
            soup = BeautifulSoup(resp.text, "html.parser")
            og_title = soup.find("meta", property="og:title")
            og_desc = soup.find("meta", property="og:description")
            og_image = soup.find("meta", property="og:image")
            if og_title:
                title_en = og_title.get("content", title_en)
            if og_desc:
                description = og_desc.get("content", "")
            if og_image:
                image_url = og_image.get("content", "")
        except Exception as exc:
            print(f"  [supplement] scrape failed for {item['url']}: {exc}")

        articles.append(
            {
                "title": title_en or item["title_fa"],
                "description": description,
                "url": item["url"],
                "source": item["source"],
                "published": datetime.now(timezone.utc).isoformat(),
                "image_url": image_url,
                "video_url": "",
                "title_fa": item["title_fa"],
                "summary_fa": item["summary_fa"],
            }
        )
        existing_urls.add(item["url"])

    return articles
