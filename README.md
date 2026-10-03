# Video Hub 18+ — Starter Project

বাংলা/English Telegram bot + responsive website starter.

## Included
- Responsive Bengali/English website
- 18+ age confirmation screen
- Six-step ad placement demo
- Admin login and video catalogue
- Telegram bot commands: `/start`, `/videos`, `/watch ID`
- SQLite database

## Important before publishing
1. This starter does **not** contain videos or real ad-network integration.
2. `ADS_DEMO_MODE=true` is only a local/demo gate. It does not verify real ad views and must not be used to claim genuine ad completion.
3. For real ads, integrate an ad provider that supports a signed server-to-server completion callback. Then set `ADS_DEMO_MODE=false` and implement that provider's callback in `app.py`.
4. Only publish lawful content featuring consenting adults (18+). Do not upload content involving minors, non-consensual material, hidden-camera recordings, or content you do not have rights to distribute.
5. Do not expose bot tokens, passwords, or `.env` files. Keep secrets in your hosting provider's Environment settings.

## GitHub upload
Upload the contents of this ZIP into the root of your `video-hub-18` repository. Replace existing `app.py`, `requirements.txt`, and `README.md`, and add all other files/folders. Commit directly to `main`.

## Deploy on Render
1. Create a new **Web Service** and connect this GitHub repository.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Add environment variables:
   - `BOT_TOKEN` = token from BotFather
   - `WEBAPP_URL` = your deployed HTTPS URL
   - `ADMIN_PASSWORD` = a long unique password
   - `SECRET_KEY` = a long random secret
   - `ADS_DEMO_MODE` = `true` while testing only
5. Deploy. After the site is live, set `WEBAPP_URL` to its final URL and redeploy.

## Telegram bot
Set `BOT_TOKEN` and `WEBAPP_URL` in hosting environment variables. The bot uses polling and starts with the web process. Commands:
- `/start` — opens website
- `/videos` — lists active videos
- `/watch 1` — sends the Telegram video if its `file_id` is configured

To get a Telegram `file_id`, send the video to your bot and use a bot update/file-id inspection workflow, or use a private admin-only helper. Never post file IDs publicly.

## Add a video
Open `/admin/login`, sign in with `ADMIN_PASSWORD`, and enter a title plus either:
- Telegram `file_id`, for sending inside Telegram; or
- a direct video URL, for website playback.

## Free hosting note
Free hosting may sleep, restart, or have ephemeral storage. SQLite videos/catalogue may be lost on some free instances. Use a persistent disk or managed database for production. Some hosts restrict always-on background bot polling; if so, run the bot as a separate worker or use webhooks.

## Current limitation
The six ad cards are placeholders. The project intentionally does not fake ad impressions. A real provider's approved ad SDK/callback is required before real ad gating or monetization.
