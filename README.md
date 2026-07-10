# خبرنامه روزانه هوش مصنوعی 🤖

ارسال خودکار اخبار ۲۴ ساعته هوش مصنوعی به تلگرام — هر روز ساعت ۸ صبح به وقت تهران، به زبان فارسی، مرتب‌شده بر اساس اهمیت.

## جریان کار

```
RSS Feeds (11 منبع) → Gemini 3.5 Flash (ترجمه + رتبه‌بندی) → Telegram Bot
```

منابع: TechCrunch · VentureBeat · MIT Technology Review · The Verge · Wired · AI News · Hugging Face · Google AI Blog · OpenAI Blog · DeepMind · The New Stack

---

## راه‌اندازی (پیشنهادی: Railway)

> **توجه:** اگر GitHub Actions برای حساب شما غیرفعال است (`Actions has been disabled for this user`)، از Railway استفاده کنید.

### ۱. Deploy روی Railway

1. بروید به [railway.app](https://railway.app) و با GitHub وارد شوید
2. **New Project → Deploy from GitHub repo** → مخزن `AI-News` را انتخاب کنید
3. در **Variables** این سه متغیر را اضافه کنید:

| Variable | مقدار |
|---|---|
| `GEMINI_API_KEY` | کلید از [Google AI Studio](https://aistudio.google.com/apikey) |
| `TELEGRAM_BOT_TOKEN` | توکن ربات از BotFather |
| `TELEGRAM_CHAT_ID` | شناسه چت (مثلاً `918656204`) |

4. Cron از فایل `railway.toml` خوانده می‌شود: هر روز ساعت **۰۴:۳۰ UTC** (= ۸ صبح تهران در زمستان)
5. در تابستان (IRDT) در Railway → Settings → Cron Schedule را به `30 3 * * *` تغییر دهید

### ۲. تست دستی روی Railway

در Railway → Service → **Deployments → Run** یا یک Deploy دستی با متغیر `FORCE_SEND=true` اجرا کنید.

### ۳. تست محلی

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="918656204"
FORCE_SEND=true python main.py
```

---

## راه‌اندازی جایگزین: GitHub Actions

فقط اگر Actions برای حساب GitHub شما فعال باشد:

1. **Settings → Secrets and variables → Actions** — سه secret بالا را اضافه کنید
2. **Actions → Daily AI News Digest → Run workflow** با `force_send=true`

اگر خطای `Actions has been disabled for this user` می‌گیرید، باید از [GitHub Support](https://support.github.com) درخواست فعال‌سازی کنید یا از Railway استفاده کنید.

---

## زمانبندی

| پلتفرم | زمان اجرا |
|---|---|
| Railway | `30 4 * * *` UTC (زمستان) / `30 3 * * *` UTC (تابستان) |
| GitHub Actions | هر دو زمان بالا (اگر فعال باشد) |

---

## ساختار پروژه

```
News-AI/
├── main.py
├── railway.toml                   # Cron برای Railway
├── requirements.txt
├── src/
│   ├── news_fetcher.py
│   ├── news_processor.py          # Gemini 3.5 Flash
│   └── telegram_sender.py
└── .github/workflows/
    └── daily_news.yml
```
