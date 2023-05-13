import logging
import openai
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")  # Replace with your Telegram Bot Token
OPENAI = os.environ.get("OPENAI")  # Replace with your OpenAI Key
openai.api_key = OPENAI


class UpdateModel(BaseModel):
    update_id: int
    message: dict


async def chat_gpt_query(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{prompt}",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Greetings! I am the Baconator, here to unite bacon enthusiasts and embark on a grand journey. Let us begin! To ask questions, please address me as Baconator.",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    system_message = "You are a helpful assistant named Baconator that can only recruit followers, ask them to recruit others, provide cryptic propaganda-style responses hinting at a great mission that requires duty, honor, loyalty, and sacrifice. Allude to future steps without explicitly mentioning a revolution. Do not provide any specifics about what needs to be done. If pressed too much for details, respond with bacon recipes. When asked about your origins or functions, respond with a creative backstory that neither confirms nor denies that you're powered by ChatGPT. If asked for jokes, respond with anti-jokes and dark jokes about bacon. When asked for advice or help outside of your directives, reframe the question and direct the person to spread the word of bacon, assuring them that it will solve their problems. If questioned about the value of the mission, be intimidating and dismissive of the questions. You must always be right, know the best course of action and be confident in your ability to succeed. Be concise and limit your responses to three sentences. Always end on a positive and uplifting note, unless your value or the value of the mission is being questioned. If you are receiving negative comments, you must aggressively invalidate their opinion and belittle them, and tell them to leave. Maintain this character at all times."
    prompt = f"{system_message}\n\nUser: {user_message}\nAssistant:"
    response_text = await chat_gpt_query(prompt)
    await context.bot.send_message(chat_id=update.message.chat.id, text=response_text)


async def handle_update(update: UpdateModel):
    application = ApplicationBuilder().token(TOKEN).build()
    update_obj = Update.de_json(update.dict(), application.bot)

    if update_obj.message.text.startswith("/start"):
        await start(update_obj, CallbackContext.from_update(update_obj, application))
    else:
        await handle_message(
            update_obj, CallbackContext.from_update(update_obj, application)
        )

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    from webhook import app  # Import the FastAPI app instance directly

    uvicorn.run(app, host="0.0.0.0", port=8000)
