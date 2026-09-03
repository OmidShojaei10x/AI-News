# هشدار هوشمند اخبار هوش مصنوعی

بررسی خودکار اخبار AI **۳ بار در روز** (۹:۰۰، ۱۲:۰۰، ۲۱:۰۰ به وقت تهران) با **Cursor Automation + Composer**.

فقط خبرهای **مهم** (۰ تا ۳) به کانال تلگرام ارسال می‌شوند. همه بررسی‌ها در Supabase لاگ می‌شوند.

## جریان کار

```
RSS Feeds → Composer (فیلتر + ترجمه فارسی) → Supabase → کانال تلگرام
```

- **پردازش هوشمند:** Composer (مدل Cursor) — **بدون Gemini API**
- **۹ صبح:** بازه ۲۴ ساعت گذشته
- **۱۲ ظهر و ۲۱ شب:** بازه ۸ ساعت گذشته
- **بدون خبر مهم:** فقط لاگ در Supabase

پرامپت اتوماسیون: [`AUTOMATION_PROMPT.md`](AUTOMATION_PROMPT.md)

---

## اجرا (Cursor Automation)

۱. `python scripts/fetch_articles.py` — جمع‌آوری اخبار
۲. Composer اخبار مهم را انتخاب و به فارسی ترجمه می‌کند
۳. `python scripts/publish_articles.py` — ذخیره + ارسال به کانال
۴. یا `python scripts/log_check.py` — فقط لاگ (بدون خبر مهم)

---

## متغیرهای محیطی

| Variable | توضیح |
|---|---|
| `TELEGRAM_BOT_TOKEN` | توکن ربات از BotFather |
| `TELEGRAM_CHAT_ID` | کانال: `-1004366053988` ([اخبار هوش مصنوعی](https://t.me/+JPVZfc1WuRQ3NGRk)) |
| `SUPABASE_URL` | آدرس پروژه Supabase |
| `SUPABASE_ANON_KEY` | کلید anon/publishable Supabase |
| `CHECK_SLOT` | `morning` / `noon` / `evening` (اختیاری) |

---

## زمانبندی Cron (UTC)

| بازه | ۹ صبح | ۱۲ ظهر | ۲۱ شب |
|---|---|---|---|
| زمستان (IRST) | `30 5 * * *` | `30 8 * * *` | `30 17 * * *` |
| تابستان (IRDT) | `30 4 * * *` | `30 7 * * *` | `30 16 * * *` |

---

## ساختار پروژه

```
AI-News/
├── AUTOMATION_PROMPT.md    # پرامپت اتوماسیون Cursor
├── main.py                 # تشخیص check_slot
├── scripts/
│   ├── fetch_articles.py   # جمع‌آوری RSS
│   ├── publish_articles.py # ذخیره + ارسال
│   └── log_check.py        # لاگ بدون ارسال
└── src/
    ├── news_fetcher.py
    ├── supabase_storage.py
    └── telegram_sender.py
```
