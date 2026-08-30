# خبرنامه روزانه هوش مصنوعی 🤖

ارسال خودکار اخبار ۲۴ ساعته هوش مصنوعی به تلگرام — هر روز ساعت ۸ صبح به وقت تهران، به زبان فارسی، مرتب‌شده بر اساس اهمیت.

## جریان کار

```
RSS Feeds (11 منبع) → Gemini 3.5 Flash (ترجمه + رتبه‌بندی) → Supabase → Telegram Bot
```

---

## راه‌اندازی رایگان (پیشنهادی)

> GitHub Actions و Railway برای شما کار نمی‌کنند (Actions غیرفعال / Railway پولی).  
> دو راه **کاملاً رایگان** زیر را پیشنهاد می‌کنیم.

### گزینه ۱: PythonAnywhere (ساده‌ترین — بدون کارت بانکی)

1. ثبت‌نام رایگان در [pythonanywhere.com](https://www.pythonanywhere.com)
2. تب **Consoles → Bash**:
   ```bash
   git clone https://github.com/OmidShojaei10x/AI-News.git
   cd AI-News
   pip install --user -r requirements.txt
   ```
3. تب **Web → Files** یا Bash — فایل `.env` بسازید:
   ```
   GEMINI_API_KEY=کلید-جمینای
   TELEGRAM_BOT_TOKEN=توکن-ربات
   TELEGRAM_CHAT_ID=918656204
   FORCE_SEND=true
   ```
4. تب **Tasks** → **Create a new scheduled task**:
   - زمان: `04:30` (UTC) = ۸ صبح تهران (زمستان)
   - دستور:
     ```bash
     cd ~/AI-News && export $(cat .env | xargs) && python main.py
     ```
5. تب **Web → Allowlisted sites** — این دامنه‌ها را اضافه کنید:
   - `generativelanguage.googleapis.com`
   - `api.telegram.org`
   - `techcrunch.com`, `venturebeat.com`, `technologyreview.com`, `theverge.com`, `wired.com`, `artificialintelligence-news.com`, `huggingface.co`, `blog.google`, `openai.com`, `deepmind.google`, `thenewstack.io`

**تست:** در Bash اجرا کنید:
```bash
cd ~/AI-News && export $(cat .env | xargs) && python main.py
```

---

### گزینه ۲: Render Cron Job

1. بروید به [render.com](https://render.com) → **New +** → **Cron Job**
2. مخزن GitHub `AI-News` را وصل کنید
3. این مقادیر را وارد کنید:

| فیلد | مقدار |
|---|---|
| **Build Command** | `pip install -r requirements.txt` |
| **Schedule** | `30 4 * * *` |
| **Command** | `python main.py` |

4. در **Environment Variables** اضافه کنید:

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | کلید Gemini |
| `TELEGRAM_BOT_TOKEN` | توکن ربات |
| `TELEGRAM_CHAT_ID` | `918656204` |

5. **Instance Type**: Starter کافی است
6. **Create Cron Job** → بعد از Deploy روی **Trigger Run** بزنید برای تست

> **هزینه:** Cron Job در Render پولی است (حدود \$0.01 در روز).  
> **زمان:** `30 4 * * *` = ۰۸:۰۰ صبح تهران (زمستان). در تابستان: `30 3 * * *`

یا با Blueprint: **New → Blueprint** → مخزن را وصل کنید — `render.yaml` آماده است.

---

### گزینه ۳: Render Web (رایگان) + cron-job.org

اگر Cron پولی Render را نمی‌خواهید، از `trigger_server.py` با پلن Free Web + [cron-job.org](https://cron-job.org) استفاده کنید (جزئیات در نسخه قبلی README).

---

## تست محلی (هر زمان)

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="918656204"
FORCE_SEND=true python main.py
```

---

## متغیرهای محیطی

| Variable | توضیح |
|---|---|
| `GEMINI_API_KEY` | کلید از [Google AI Studio](https://aistudio.google.com/apikey) |
| `TELEGRAM_BOT_TOKEN` | توکن ربات از BotFather |
| `TELEGRAM_CHAT_ID` | شناسه چت (مثلاً `918656204`) |
| `SUPABASE_URL` | آدرس پروژه Supabase |
| `SUPABASE_ANON_KEY` | کلید anon پروژه Supabase |
| `FORCE_SEND` | `true` برای ارسال فوری بدون چک ساعت |
| `CRON_SECRET` | فقط برای `trigger_server.py` (Render + cron-job) |

---

## زمانبندی

| فصل | Cron (UTC) | معادل تهران |
|---|---|---|
| زمستان | `30 4 * * *` | ۰۸:۰۰ |
| تابستان | `30 3 * * *` | ۰۸:۰۰ |

---

## ساختار پروژه

```
AI-News/
├── main.py                 # اجرای مستقیم
├── trigger_server.py       # HTTP trigger برای cron-job.org
├── render.yaml             # Deploy رایگان Render
├── railway.toml            # (اختیاری — نیاز به پلن پولی)
└── src/
    ├── news_fetcher.py
    ├── news_processor.py   # Gemini 3.5 Flash
    ├── news_supplement.py  # تکمیل اخبار + ترجمه فارسی
    ├── supabase_store.py   # ذخیره در Supabase
    └── telegram_sender.py
```
