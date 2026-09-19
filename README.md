# vir2oz Telegram bot — Vercel ready

## Vercel Environment Variables

Set:
- `TELEGRAM_BOT_TOKEN` — token from @BotFather
- `OPENAI_API_KEY` — OpenAI API key
- `OPENAI_MODEL` — optional model name available to your API key

## Telegram webhook

After deployment, set the webhook to:
`https://YOUR-DOMAIN.vercel.app/api/webhook`

You can set it with Telegram Bot API `setWebhook`.

The bot accepts `/vir2oz your question` and ordinary text messages.
