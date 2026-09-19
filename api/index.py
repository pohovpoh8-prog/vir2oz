import os
import logging
from fastapi import FastAPI, Request
from openai import AsyncOpenAI
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vir2oz")

app = FastAPI()


def get_clients():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    key = os.getenv("OPENAI_API_KEY")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return Bot(token=token), AsyncOpenAI(api_key=key)


async def send_long(bot, chat_id, text):
    for i in range(0, len(text), 4096):
        await bot.send_message(chat_id=chat_id, text=text[i:i + 4096])


@app.get("/api")
async def status():
    return {"status": "ok", "service": "vir2oz-bot"}


@app.get("/api/webhook")
async def webhook_status():
    return {"status": "ok", "service": "vir2oz-webhook"}


@app.post("/api/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id:
        return {"ok": True}

    # Only /v2 and /v2@BotName are handled.
    if not text.startswith("/"):
        return {"ok": True}

    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    base_command = command.split("@", 1)[0]

    if base_command != "/v2":
        return {"ok": True}

    question = parts[1].strip() if len(parts) > 1 else ""
    bot, client = get_clients()

    if not question:
        await bot.send_message(
            chat_id=chat_id,
            text="Напиши вопрос после /v2 🙂"
        )
        return {"ok": True}

    try:
        model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
        response = await client.responses.create(
            model=model,
            input=question,
        )
        answer = (response.output_text or "").strip()
        if not answer:
            answer = "Не удалось получить ответ."
        await send_long(bot, chat_id, answer)
    except Exception:
        logger.exception("OpenAI/Telegram error")
        await bot.send_message(
            chat_id=chat_id,
            text="Ошибка при обработке запроса. Проверь ключи и логи Vercel."
        )

    return {"ok": True}
