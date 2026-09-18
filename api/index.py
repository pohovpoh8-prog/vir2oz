import os

from fastapi import FastAPI, Request
from openai import AsyncOpenAI
from telegram import Bot

app = FastAPI()


def get_clients():
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    return Bot(token=telegram_token), AsyncOpenAI(api_key=openai_key)


async def send_long_message(bot: Bot, chat_id: int, text: str) -> None:
    # Telegram limits a message to 4096 characters.
    for i in range(0, len(text), 4096):
        await bot.send_message(chat_id=chat_id, text=text[i:i + 4096])


@app.get("/")
async def root():
    return {"status": "ok", "service": "vir2oz-bot"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message") or {}

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or ""

    if not chat_id or not text.startswith("/vir2oz"):
        return {"ok": True}

    question = text[len("/vir2oz"):].strip()

    if not question:
        await get_clients()[0].send_message(
            chat_id=chat_id,
            text="Напиши вопрос после /vir2oz 🙂",
        )
        return {"ok": True}

    bot, client = get_clients()

    response = await client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        input=question,
    )

    answer = response.output_text or "Не удалось получить ответ."
    await send_long_message(bot, chat_id, answer)

    return {"ok": True}
