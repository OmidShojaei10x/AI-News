# هشدار هوشمند اخبار هوش مصنوعی

بررسی خودکار اخبار AI **۳ بار در روز** (۹:۰۰، ۱۲:۰۰، ۲۱:۰۰ به وقت تهران). فقط خبرهای **مهم** (۰ تا ۳) به تلگرام ارسال می‌شوند. همه بررسی‌ها در Supabase لاگ می‌شوند.

## جریان کار

```
RSS Feeds → ددآپ (Supabase) → Gemini (فیلتر اهمیت) → Supabase → Telegram
```

- **۹ صبح:** بازه ۲۴ ساعت گذشته
- **۱۲ ظهر و ۲۱ شب:** بازه ۸ ساعت گذشته
- **بدون خبر مهم:** فقط لاگ در Supabase، بدون پیام تلگرام

پرامپت اتوماسیون Cursor: [`AUTOMATION_PROMPT.md`](AUTOMATION_PROMPT.md)

---

## تست محلی

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="918656204"
export SUPABASE_URL="https://uwpkiioexphefbiddmmf.supabase.co"
export SUPABASE_ANON_KEY="..."
CHECK_SLOT=morning FORCE_SEND=true python main.py
```

`CHECK_SLOT` می‌تواند `morning`، `noon` یا `evening` باشد.

---

## متغیرهای محیطی

| Variable | توضیح |
|---|---|
| `GEMINI_API_KEY` | کلید از [Google AI Studio](https://aistudio.google.com/apikey) |
| `TELEGRAM_BOT_TOKEN` | توکن ربات از BotFather |
| `TELEGRAM_CHAT_ID` | شناسه چت (مثلاً `918656204`) |
| `SUPABASE_URL` | آدرس پروژه Supabase |
| `SUPABASE_ANON_KEY` | کلید anon/publishable Supabase |
| `CHECK_SLOT` | `morning` / `noon` / `evening` (اختیاری) |
| `FORCE_SEND` | `true` برای اجرا بدون چک پنجره زمانی |
| `CRON_SECRET` | فقط برای `trigger_server.py` |

---

## زمانبندی (UTC)

| بازه | ۹ صبح | ۱۲ ظهر | ۲۱ شب |
|---|---|---|---|
| زمستان (IRST) | `30 5 * * *` | `30 8 * * *` | `30 17 * * *` |
| تابستان (IRDT) | `30 4 * * *` | `30 7 * * *` | `30 16 * * *` |

---

## ساختار پروژه

```
AI-News/
├── main.py                 # اجرای بررسی هوشمند
├── AUTOMATION_PROMPT.md    # پرامپت اتوماسیون Cursor
├── trigger_server.py       # HTTP trigger برای cron-job.org
├── render.yaml             # ۳ Cron Job (صبح/ظهر/شب)
└── src/
    ├── news_fetcher.py     # RSS + OG image
    ├── news_processor.py   # Gemini فیلتر اهمیت
    ├── supabase_storage.py # ذخیره + ددآپ + لاگ
    └── telegram_sender.py  # ارسال هشدار تکی
```
