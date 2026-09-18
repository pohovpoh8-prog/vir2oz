# vir2oz Telegram bot for Vercel

## Environment variables

Add these variables in Vercel Project Settings -> Environment Variables:

- `TELEGRAM_BOT_TOKEN` — token from @BotFather
- `OPENAI_API_KEY` — OpenAI API key
- `OPENAI_MODEL` — optional; defaults to `gpt-5.6-luna`

## Deploy

Import this folder/ZIP into Vercel and deploy.

After deployment, the webhook endpoint is:

`https://YOUR-DOMAIN.vercel.app/api/webhook`

Set the Telegram webhook to that URL, for example:

`https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=https://YOUR-DOMAIN.vercel.app/api/webhook`

The bot responds to `/vir2oz your question`.
