# vir2oz — Telegram bot on Vercel

Готовая serverless-версия Telegram-бота для Vercel.

## Что изменено

- FastAPI оставлен как HTTP-приложение, которое Vercel умеет деплоить напрямую.
- Webhook находится на `POST /webhook`.
- Telegram API вызывается напрямую через `httpx`; отдельный polling-процесс не нужен.
- Добавлена опциональная защита webhook через `TELEGRAM_WEBHOOK_SECRET`.
- Добавлен `/health`.
- Добавлен `GET /webhook` для проверки.
- Добавлен `204 /favicon.ico`, чтобы браузер не создавал лишний `404`.
- Команда бота: `/v2 твой вопрос`.
- Ответы длиннее 4096 символов автоматически разбиваются на несколько сообщений.

## 1. Переменные Vercel

В Project Settings → Environment Variables добавь:

```text
TELEGRAM_BOT_TOKEN=токен_от_BotFather
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.6-luna
TELEGRAM_WEBHOOK_SECRET=случайная_длинная_строка
```

`OPENAI_MODEL` можно не задавать: используется `gpt-5.6-luna`.

`TELEGRAM_WEBHOOK_SECRET` тоже можно не задавать, но для публичного webhook рекомендуется задать.

После изменения Environment Variables сделай новый Deploy.

## 2. Деплой

Загрузи содержимое этого архива как отдельный Vercel Project.

Vercel должен определить `app.py` как FastAPI-приложение автоматически.

После деплоя, например:

```text
https://ТВОЙ-ПРОЕКТ.vercel.app/
https://ТВОЙ-ПРОЕКТ.vercel.app/health
https://ТВОЙ-ПРОЕКТ.vercel.app/webhook
```

`/health` должен вернуть:

```json
{"status":"ok"}
```

## 3. Установить Telegram webhook

Выполни один раз:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=https://ТВОЙ-ПРОЕКТ.vercel.app/webhook" \
  -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```

Если `TELEGRAM_WEBHOOK_SECRET` не используется:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=https://ТВОЙ-ПРОЕКТ.vercel.app/webhook"
```

Проверить webhook:

```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

В ответе Telegram `url` должен указывать на твой Vercel `/webhook`.

## 4. Проверка

Открой:

```text
https://ТВОЙ-ПРОЕКТ.vercel.app/
https://ТВОЙ-ПРОЕКТ.vercel.app/health
https://ТВОЙ-ПРОЕКТ.vercel.app/webhook
```

Затем в Telegram отправь:

```text
/v2 Привет
```

## Важно

Не запускай одновременно старую polling-версию (`bot.py`, `run_polling()` и т.п.) и этот webhook для одного Telegram-бота.

Для Vercel нужен именно webhook: Telegram отправляет update на `/webhook`, Vercel запускает функцию, она вызывает OpenAI и отправляет ответ обратно в Telegram.
