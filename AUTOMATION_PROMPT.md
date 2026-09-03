# هشدار هوشمند اخبار هوش مصنوعی

## هدف
۳ بار در روز (۹:۰۰، ۱۲:۰۰، ۲۱:۰۰ به وقت تهران) اخبار AI را بررسی کن.
فقط اگر خبر **مهم** پیدا شد به تلگرام اطلاع بده (۰ تا ۳ خبر).
همه بررسی‌ها — حتی بدون خبر — در Supabase لاگ شوند.

## Skills (قبل از شروع بخوان)
- Supabase: `$HOME/.cursor/plugins/cache/cursor-public/652/release_v0.1.4/skills/supabase/SKILL.md`
- Supabase Postgres Best Practices
- Walkthrough Artifacts (برای اثبات ارسال)
- Subscribe (برای رویدادهای CI/PR در صورت نیاز)
- Env Setup (اگر env vars ناقص بود)

## حافظه
ابتدا `/cursor/stores/automation/memories/MEMORIES.md` را بخوان و در پایان به‌روزرسانی کن.

## متغیرهای محیطی (هرگز در خروجی لو نده)
- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID` — کانال اخبار هوش مصنوعی: `-1004366053988` (https://t.me/+JPVZfc1WuRQ3NGRk)
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

اگر هر کدام نبود، از Skill Env Setup کمک بگیر.

## Supabase
- پروژه: `ai-news-telegram` (`uwpkiioexphefbiddmmf`)
- جدول اخبار: `public.ai_news`
- جدول لاگ بررسی: `public.ai_news_checks`

## گام‌ها

### ۱. تعیین بازه زمانی
بر اساس ساعت فعلی تهران:
- اگر نزدیک ۹ صبح → `lookback = 24` ساعت (`check_slot = morning`)
- اگر نزدیک ۱۲ ظهر → `lookback = 8` ساعت (`check_slot = noon`)
- اگر نزدیک ۲۱ شب → `lookback = 8` ساعت (`check_slot = evening`)

### ۲. جمع‌آوری اخبار
از RSS feeds پروژه (`src/news_fetcher.py`) اخبار بازه را بگیر.
اگر `image_url` خالی بود، OG image صفحه خبر را scrape کن.

### ۳. فیلتر ددآپ
از Supabase URLهایی که `sent_to_telegram = true` دارند را بخوان و حذف کن.

### ۴. فیلتر اهمیت (Gemini)
فقط این دسته‌ها «مهم» هستند:
- معرفی مدل/محصول جدید (OpenAI, Google, Anthropic, Meta, ...)
- ادغام، خرید، یا سرمایه‌گذاری بزرگ
- قوانین و تصمیمات دولتی
- حوادث امنیتی/ایمنی AI
- رقابت و همکاری‌های استراتژیک مهم
- تحقیقات برجسته با تأثیر صنعتی

**خبرهای معمولی، تبلیغاتی، یا رویدادهای کوچک را رد کن.**
اگر هیچ خبر مهمی نبود → آرایه خالی برگردان.

حداکثر ۳ خبر مهم. برای هر خبر:
- `title_fa`: عنوان فارسی
- `summary_fa`: خلاصه ۲–۴ جمله‌ای فارسی
- `importance_rank`: ۱ = مهم‌ترین

### ۵. ذخیره در Supabase
- اگر خبر مهم بود: در `ai_news` ذخیره کن (`check_slot`: morning/noon/evening)
- همیشه: یک ردیف در `ai_news_checks` با `articles_found`, `articles_sent`, `check_slot`

### ۶. ارسال تلگرام (کانال)
**مقصد:** کانال «اخبار هوش مصنوعی» — `TELEGRAM_CHAT_ID=-1004366053988`
**فقط اگر خبر مهم بود:**
- هر خبر = یک پیام جدا
- اگر عکس دارد: `sendPhoto` با caption فارسی
- اگر نه: `sendMessage`
- فرمت: عنوان + خلاصه + منبع + لینک
- بعد از ارسال: `sent_to_telegram = true`

**اگر خبر مهمی نبود: به تلگرام چیزی نفرست.**

### ۷. به‌روزرسانی حافظه
در `MEMORIES.md` ثبت کن: آخرین بررسی، تعداد ارسال‌شده، عنوان اخبار.

## قوانین
- هرگز یک URL را دوباره نفرست
- حداکثر ۳ خبر در هر بررسی
- همه متن‌ها فارسی
- توکن‌ها و کلیدها را در commit/PR/پیام لو نده
- اگر کد نیاز به تغییر دارد، PR باز کن

## Cron (UTC)

| بازه | ۹ صبح تهران | ۱۲ ظهر تهران | ۲۱ شب تهران |
|------|-------------|--------------|-------------|
| زمستان (IRST) | `30 5 * * *` | `30 8 * * *` | `30 17 * * *` |
| تابستان (IRDT) | `30 4 * * *` | `30 7 * * *` | `30 16 * * *` |
