import os

from fastapi import FastAPI, Request
from openai import OpenAI
from telegram import Bot


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing")


client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/api/webhook")
async def webhook(request: Request):
    data = await request.json()

    message = data.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if not text.startswith("/vir2oz"):
        return {"ok": True}

    question = text[len("/vir2oz"):].strip()

    if not question:
        await bot.send_message(
            chat_id=chat_id,
            text="Напиши вопрос после /vir2oz 🙂"
        )
        return {"ok": True}

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=question,
    )

    await bot.send_message(
        chat_id=chat_id,
        text=response.output_text,
    )

    return {"ok": True}