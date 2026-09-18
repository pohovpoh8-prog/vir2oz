import os

from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


async def vir2oz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Если после /vir2oz написан текст
    question = " ".join(context.args).strip()

    # Если /vir2oz используется как ответ на другое сообщение
    if not question and message.reply_to_message:
        question = message.reply_to_message.text or ""

    # Если вопроса вообще нет
    if not question:
        await message.reply_text(
            "Напиши вопрос после /vir2oz или используй /vir2oz "
            "в ответ на сообщение 🙂"
        )
        return

    # Отправляем вопрос в OpenAI
    response = client.responses.create(
        model="gpt-5.6-luna",
        input=question
    )

    answer = response.output_text

    await message.reply_text(answer)


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("vir2oz", vir2oz))

    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()