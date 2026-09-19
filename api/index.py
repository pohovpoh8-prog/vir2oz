import os
import logging

from fastapi import FastAPI, Request
from openai import AsyncOpenAI
from telegram import Bot

app = FastAPI()
logger = logging.getLogger("vir2oz")


def get_clients():
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    return Bot(token=telegram_token), AsyncOpenAI(api_key=openai_key)


async def send_long_message(bot: Bot, chat_id: int, text: str):
    for start in range(0, len(text), 4096):
        await bot.send_message(chat_id=chat_id, text=text[start:start + 4096])


@app.get("/api")
async def api_status():
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

    # Only /v2 and /v2@BotName are accepted.
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

        await send_long_message(bot, chat_id, answer)

    except Exception:
        logger.exception("Error while processing /v2")
        await bot.send_message(
            chat_id=chat_id,
            text="Ошибка при обработке запроса. Проверь OPENAI_API_KEY, "
                 "OPENAI_MODEL и логи Vercel."
        )

    return {"ok": True}
