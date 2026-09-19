# vir2oz — Vercel

Структура:
- app.py
- requirements.txt
- README.md

Environment Variables в Vercel:
- TELEGRAM_BOT_TOKEN
- OPENAI_API_KEY
- OPENAI_MODEL (необязательно; по умолчанию gpt-5.6-luna)

После Deploy Telegram webhook должен быть:
https://vir2oz-r7ir.vercel.app/webhook

Проверка:
https://vir2oz-r7ir.vercel.app/webhook

Ожидаемый ответ:
{"status":"ok","service":"vir2oz-webhook"}

Команда в Telegram:
 /v2 Привет

Не запускайте одновременно polling-версию bot.py и webhook-версию Vercel для одного бота.
