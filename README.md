# Video Hub 18+ — Starter Project

বাংলা/English Telegram Bot + Telegram Mini App starter.

## কী আছে
- FastAPI backend ও Telegram Bot (aiogram)
- Telegram Mini App-এর `initData` server-side validation
- Telegram-এ থাকা ভিডিও `file_id` দিয়ে পাঠানো
- ৬টি বৈধ rewarded-ad completion-এর server-side progress interface
- 18+ age confirmation screen (এটি আইনগত age verification-এর বিকল্প নয়)
- Admin API দিয়ে ভিডিও যোগ করা (শুধু Telegram `file_id`, title, category)

## গুরুত্বপূর্ণ
এই starter-এ বিজ্ঞাপন নেটওয়ার্কের আসল integration দেওয়া নেই। `app/ads.py`-তে provider-এর server-to-server callback যাচাই করে তবেই completion credit দিন। কেবল বাটনে ক্লিক, countdown বা redirect-কে ad view হিসেবে গণনা করবেন না। এমন ad network ব্যবহার করুন যার শর্তে rewarded/incentivized traffic স্পষ্টভাবে অনুমোদিত।

শুধু আইনসম্মত, সম্মতিপূর্ণ, প্রাপ্তবয়স্কদের কনটেন্ট ব্যবহার করুন। অপ্রাপ্তবয়স্ক, গোপন ক্যামেরা, জবরদস্তি, non-consensual বা অন্যের অধিকার লঙ্ঘনকারী কনটেন্ট আপলোড/বিতরণ করবেন না। আপনার দেশ, hosting provider, Telegram এবং ad provider-এর নিয়ম যাচাই করুন।

## চালানো
1. Python 3.11+ ইনস্টল করুন।
2. `cp .env.example .env` করে token, URL, admin ID সেট করুন।
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. অন্য টার্মিনালে `python -m app.bot`

## ভিডিও যোগ
Telegram-এ বটকে ভিডিও পাঠিয়ে `file_id` সংগ্রহ করুন (এই starter-এ bot-এর `/fileid` কমান্ড ভিডিওর `file_id` দেখায়)। তারপর admin API-তে:
`POST /api/admin/videos`
Header: `X-Admin-Key: <ADMIN_KEY>`
JSON: `{"title":"Sample","category":"General","telegram_file_id":"...","thumbnail_url":""}`

## Telegram Mini App সেটআপ
- BotFather-এ Mini App/Web App URL হিসেবে HTTPS ওয়েবসাইট URL সেট করুন।
- `.env`-এ `WEBAPP_URL` দিন।
- Frontend-এ Telegram WebApp SDK যুক্ত আছে।
- Production-এ HTTPS, persistent database, rate limiting, logging, backup, privacy policy, terms, age gate/age assurance এবং ad provider callback verification যোগ করুন।

## সীমাবদ্ধতা
এটি একটি নিরাপদ starter scaffold, production-ready hosting বা পূর্ণ ad-network integration নয়। ডিফল্ট database SQLite; production-এ PostgreSQL ব্যবহার করুন।
