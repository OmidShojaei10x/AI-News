# حافظهٔ اتوماسیون اخبار AI

## پروژه
- مخزن: `OmidShojaei10x/AI-News`
- Supabase: `ai-news-telegram` (`uwpkiioexphefbiddmmf`)
- جداول: `public.ai_news`, `public.ai_news_checks`
- کانال تلگرام: `-1004366053988` (متغیر `TELEGRAM_CHAT_ID`)

## گردش کار (۳ بار در روز — Composer، بدون Gemini API)
1. `python3 scripts/fetch_articles.py` → `/tmp/fetched_articles.json`
2. Agent اخبار را برای اهمیت فیلتر و فارسی می‌کند (حداکثر ۳)
3. اگر مهم: `python3 scripts/publish_articles.py prepared.json --slot SLOT --lookback H --found N`
4. اگر نه: `python3 scripts/log_check.py --slot SLOT --lookback H --found N --sent 0`

## اسلات‌ها (وقت تهران)
| اسلات | ساعت | lookback |
|--------|------|----------|
| morning | ۸–۱۱ | ۲۴h |
| noon | ۱۱–۱۸ | ۸h |
| evening | ۱۸+ | ۸h |

## معیار «خبر مهم»
معرفی مدل/محصول بزرگ، M&A یا سرمایه‌گذاری بزرگ، قوانین دولتی، حادثه امنیتی AI، رقابت استراتژیک، تحقیق برجسته. تبلیغات، گجت مصرفی، یادداشت نظری بدون رویداد جدید → ارسال نمی‌شود.

## آخرین اجرا
- **2026-09-19 16:30 UTC** (۲۰:۰۰ تهران، اسلات `evening`)
- ۴ مقالهٔ جدید (همه TechCrunch، ۸ ساعت گذشته)
- **۰ ارسال** — هیچ‌کدام معیار هشدار را نداشتند
- لاگ: `ai_news_checks` با `found=4`, `sent=0`

## یادداشت فنی
- اسکریپت‌ها در `scripts/` (شاخهٔ cursor automation)
- env لازم: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- URLهای قبلاً در `ai_news` از fetch حذف می‌شوند
