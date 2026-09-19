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


async def send_long_message(bot: Bot, chat_id: int, text: str):
    for i in range(0, len(text), 4096):
        await bot.send_message(chat_id=chat_id, text=text[i:i + 4096])


@app.get("/")
async def health():
    return {"status": "ok", "service": "vir2oz-webhook"}


@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id:
        return {"ok": True}

    # Support /vir2oz, /vir2oz@botname, and ordinary text messages.
    command = text.split(maxsplit=1)[0].lower() if text.startswith("/") else ""
    if command.startswith("/vir2oz"):
        question = text.split(maxsplit=1)[1].strip() if len(text.split(maxsplit=1)) > 1 else ""
        if not question:
            bot, _ = get_clients()
            await bot.send_message(chat_id=chat_id, text="Напиши вопрос после /vir2oz 🙂")
            return {"ok": True}
    elif text:
        question = text
    else:
        return {"ok": True}

    bot, client = get_clients()
    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    response = await client.responses.create(model=model, input=question)
    answer = response.output_text or "Не удалось получить ответ."
    await send_long_message(bot, chat_id, answer)
    return {"ok": True}
