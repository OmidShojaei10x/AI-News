# هشدار هوشمند اخبار هوش مصنوعی

## هدف
۳ بار در روز (۹:۰۰، ۱۲:۰۰، ۲۱:۰۰ به وقت تهران) اخبار AI را بررسی کن.
فقط اگر خبر **مهم** پیدا شد به کانال تلگرام اطلاع بده (۰ تا ۳ خبر).
همه بررسی‌ها — حتی بدون خبر — در Supabase لاگ شوند.

## مدل پردازش
**از API جمینای استفاده نکن.**
خودت (Composer / مدل Cursor) اخبار را تحلیل، فیلتر اهمیت، ترجمه و خلاصه‌نویسی فارسی را انجام بده.

## Skills (قبل از شروع بخوان)
- Supabase: `$HOME/.cursor/plugins/cache/cursor-public/652/release_v0.1.4/skills/supabase/SKILL.md`
- Supabase Postgres Best Practices
- Walkthrough Artifacts (برای اثبات ارسال)
- Subscribe (برای رویدادهای CI/PR در صورت نیاز)
- Env Setup (اگر env vars ناقص بود)

## حافظه
ابتدا `/cursor/stores/automation/memories/MEMORIES.md` را بخوان و در پایان به‌روزرسانی کن.

## متغیرهای محیطی (هرگز در خروجی لو نده)
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
- نزدیک ۹ صبح → `lookback = 24` ساعت (`check_slot = morning`)
- نزدیک ۱۲ ظهر → `lookback = 8` ساعت (`check_slot = noon`)
- نزدیک ۲۱ شب → `lookback = 8` ساعت (`check_slot = evening`)

### ۲. جمع‌آوری اخبار (کد)
```bash
python scripts/fetch_articles.py
```
خروجی JSON شامل `check_slot`, `lookback_hours`, `articles` است.
اگر `image_url` خالی بود، OG image صفحه را scrape کن.

### ۳. فیلتر ددآپ
اسکریپت fetch خودش URLهای قبلاً ارسال‌شده را حذف می‌کند.
قبل از ارسال، دوباره از Supabase چک کن که URL تکراری نباشد.

### ۴. فیلتر اهمیت (خودت — Composer)
فقط این دسته‌ها «مهم» هستند:
- معرفی مدل/محصول جدید (OpenAI, Google, Anthropic, Meta, ...)
- ادغام، خرید، یا سرمایه‌گذاری بزرگ
- قوانین و تصمیمات دولتی
- حوادث امنیتی/ایمنی AI
- رقابت و همکاری‌های استراتژیک مهم
- تحقیقات برجسته با تأثیر صنعتی

**خبرهای معمولی، تبلیغاتی، یا رویدادهای کوچک را رد کن.**
اگر هیچ خبر مهمی نبود → فقط لاگ کن، به تلگرام چیزی نفرست.

حداکثر ۳ خبر مهم. برای هر خبر آماده کن:
- `title_fa`: عنوان فارسی
- `summary_fa`: خلاصه ۲–۴ جمله‌ای فارسی
- `importance_rank`: ۱ = مهم‌ترین
- `title_en`, `source`, `url`, `published`, `image_url`, `video_url`

### ۵. انتشار (کد)
اگر خبر مهم داری، JSON را به اسکریپت publish بده:
```bash
python scripts/publish_articles.py << 'EOF'
{
  "check_slot": "morning",
  "lookback_hours": 24,
  "articles_found": 15,
  "articles": [...]
}
EOF
```

اگر خبر مهمی نیست، فقط لاگ کن:
```bash
python scripts/log_check.py --slot morning --lookback 24 --found 15 --sent 0
```

### ۶. ارسال تلگرام (کانال)
**مقصد:** کانال «اخبار هوش مصنوعی» — `TELEGRAM_CHAT_ID=-1004366053988`
- هر خبر = یک پیام جدا با عکس (در صورت وجود)
- فرمت: عنوان + خلاصه فارسی + منبع + لینک
- ربات باید ادمین کانال با مجوز Post Messages باشد

### ۷. به‌روزرسانی حافظه
در `MEMORIES.md` ثبت کن: آخرین بررسی، تعداد ارسال‌شده، عنوان اخبار.

## قوانین
- **هرگز از Gemini API استفاده نکن** — پردازش با Composer انجام شود
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
