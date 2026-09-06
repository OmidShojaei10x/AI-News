# هشدار هوشمند اخبار هوش مصنوعی

## هدف
۳ بار در روز (۹:۰۰، ۱۲:۰۰، ۲۱:۰۰ به وقت تهران) اخبار AI را بررسی کن.
فقط اگر خبر **مهم** پیدا شد به کانال تلگرام اطلاع بده (۰ تا ۳ خبر).
همه بررسی‌ها — حتی بدون خبر — در Supabase لاگ شوند.

## مدل پردازش
**از API جمینای استفاده نکن.**
خودت (Composer) اخبار را تحلیل، فیلتر اهمیت، ترجمه و خلاصه‌نویسی فارسی را انجام بده.

## Skills (قبل از شروع بخوان)
- Supabase
- Supabase Postgres Best Practices
- Walkthrough Artifacts
- Subscribe
- Env Setup

## حافظه
ابتدا MEMORIES.md را بخوان و در پایان به‌روزرسانی کن.

## متغیرهای محیطی (هرگز در خروجی لو نده)
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID = -1004366053988 (کانال اخبار هوش مصنوعی)
- SUPABASE_URL
- SUPABASE_ANON_KEY

## Supabase
- پروژه: ai-news-telegram (uwpkiioexphefbiddmmf)
- جداول: public.ai_news, public.ai_news_checks

## گام‌ها

### ۰. اطمینان از اسکریپت‌ها
اگر `scripts/` وجود ندارد، از branch فعلی checkout کن (نه branch قدیمی).

### ۱. جمع‌آوری اخبار
```bash
python3 scripts/fetch_articles.py
```
- در ابتدای fetch، `publish_scheduled.py` اخبار زمان‌بندی‌شده را ارسال می‌کند
- اگر بازه ۸ ساعته خالی باشد، خودکار به ۲۴ ساعت گسترش می‌یابد

### ۲. فیلتر اهمیت (خودت — Composer)
فقط خبرهای مهم: معرفی مدل/محصول، ادغام/سرمایه‌گذاری بزرگ، قوانین دولتی، حوادث امنیتی AI، رقابت استراتژیک، تحقیقات برجسته.

**قوانین فیلتر:**
- اگر fetch بعد از dedup مقاله دارد → تا ۳ خبر ارسال کن (مگر spam/نامربوط)
- خبرهای «انتظار/پیش‌انتشار» و «انتشار رسمی» جدا هستند — هر دو مهم‌اند اگر ارسال نشده باشند
- اگر ۸ ساعته خالی بود اما ۲۴ ساعته خبر ارسال‌نشده مهم دارد → ارسال کن

حداکثر ۳ خبر. اگر مهم نیست → فقط لاگ کن.

### ۳. ترجمه فارسی (RTL)
- همه متن‌ها فارسی
- **ترتیب جمله فارسی باشد** — نام‌های انگلیسی در وسط جمله، نه ابتدا
  - ✅ «مدل Astra اپن‌ای‌آی منتشر شد»
  - ❌ «OpenAI مدل Astra را منتشر کرد»
- اسکریپت `rtl_text.py` خودکار LRI/PDI را روی متن‌های لاتین اعمال می‌کند

### ۴. انتشار
اگر خبر مهم داری:
```bash
cat payload.json | python3 scripts/publish_articles.py
```

**زمان‌بندی انتشار:**
- خبر اول: **فوری**
- خبر دوم: **+۳۰ دقیق**
- خبر سوم: **+۶۰ دقیقه**
(از طریق `scheduled_at` در Supabase + `publish_scheduled.py`)

اگر نه:
```bash
python3 scripts/log_check.py --slot SLOT --lookback HOURS --found N --sent 0
```

### ۵. کانال تلگرام
مقصد: -1004366053988 — هر خبر یک پیام جدا با عکس

## قوانین
- هرگز از Gemini API استفاده نکن
- هرگز URL تکراری بفرست
- همه متن‌ها فارسی با RTL صحیح
- توکن‌ها را لو نده

## JSON نمونه برای publish
```json
{
  "check_slot": "evening",
  "lookback_hours": 24,
  "articles_found": 2,
  "articles": [
    {
      "title_fa": "عنوان فارسی",
      "summary_fa": "خلاصه فارسی ۲-۳ جمله",
      "title_en": "English title",
      "source": "TechCrunch",
      "url": "https://...",
      "published": "2026-09-06T16:45:00+00:00",
      "image_url": "https://...",
      "importance_rank": 1
    }
  ]
}
```
