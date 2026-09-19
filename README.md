# vir2oz — final Vercel version

## Environment Variables
Add in Vercel:
- TELEGRAM_BOT_TOKEN (Secret)
- OPENAI_API_KEY (Secret)
- OPENAI_MODEL (optional, default: gpt-5.6-luna)

## Routes
GET  /api
GET  /api/webhook
POST /api/webhook

## Telegram
Set webhook to:
https://YOUR-DOMAIN.vercel.app/api/webhook

Then verify with getWebhookInfo.

Bot command:
`/v2 your question`
or in groups:
`/v2@YourBotName your question`

Do not run the polling `bot.py` at the same time.
