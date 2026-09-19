# vir2oz — Vercel Telegram bot

## Environment Variables

In Vercel add:

- `TELEGRAM_BOT_TOKEN` — token from @BotFather
- `OPENAI_API_KEY` — OpenAI API key
- `OPENAI_MODEL` — optional; default is `gpt-5.6-luna`

Set the first two as Secret.

## Deploy

Push these files to GitHub and redeploy the Vercel project.

After deployment, check:

`https://YOUR-DOMAIN.vercel.app/api`

Expected:

`{"status":"ok","service":"vir2oz-bot"}`

Check the webhook endpoint:

`https://YOUR-DOMAIN.vercel.app/api/webhook`

Expected:

`{"status":"ok","service":"vir2oz-webhook"}`

## Telegram webhook

Set the Telegram webhook to:

`https://YOUR-DOMAIN.vercel.app/api/webhook`

For example:

`https://api.telegram.org/botYOUR_TOKEN/setWebhook?url=https://YOUR-DOMAIN.vercel.app/api/webhook`

Then check:

`https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo`

The `url` must be exactly the `/api/webhook` URL.

## Bot command

The bot responds to:

`/v2 your question`

and in groups:

`/v2@YourBotName your question`

Ordinary messages are ignored.

## Important

Do NOT run the CMD polling version (`python bot.py`) at the same time as this webhook version.
Telegram bots cannot use the same update stream through polling and webhook simultaneously.
