import logging
import os

import httpx
from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse, Response
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vir2oz")

app = FastAPI(title="vir2oz Telegram Bot")


def env(name: str, required: bool = True) -> str | None:
    value = os.getenv(name)
    if required and not value:
        raise RuntimeError(f"{name} is not configured")
    return value


async def telegram_api(method: str, payload: dict) -> dict:
    token = env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")

    return data


async def send_message(chat_id: int, text: str) -> None:
    # Telegram accepts at most 4096 characters in one text message.
    for start in range(0, len(text), 4096):
        await telegram_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text[start : start + 4096],
            },
        )


def check_webhook_secret(header_value: str | None) -> bool:
    expected = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if not expected:
        # Secret checking is optional for backwards compatibility.
        return True
    return header_value == expected


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "vir2oz-bot",
        "webhook": "/webhook",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/webhook")
async def webhook_status():
    return {"status": "ok", "service": "vir2oz-webhook"}


@app.get("/favicon.ico")
async def favicon():
    # Vercel/browser requests this automatically. It is not needed by the bot.
    return Response(status_code=204)


@app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if not check_webhook_secret(x_telegram_bot_api_secret_token):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)

    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "invalid json"}, status_code=400)

    message = data.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    # Ignore non-text Telegram updates and unrelated commands.
    if not chat_id or not text:
        return {"ok": True}

    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    base_command = command.split("@", 1)[0]

    if base_command != "/v2":
        return {"ok": True}

    question = parts[1].strip() if len(parts) > 1 else ""

    if not question:
        await send_message(chat_id, "Напиши вопрос после /v2 🙂")
        return {"ok": True}

    try:
        api_key = env("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

        client = AsyncOpenAI(api_key=api_key)
        response = await client.responses.create(
            model=model,
            input=question,
        )

        answer = (response.output_text or "").strip()
        if not answer:
            answer = "Не удалось получить ответ."

        await send_message(chat_id, answer)

    except Exception:
        logger.exception("OpenAI/Telegram error")
        try:
            await send_message(
                chat_id,
                "Ошибка при обработке запроса. Проверь настройки Vercel и логи.",
            )
        except Exception:
            logger.exception("Failed to send Telegram error message")

    return {"ok": True}
