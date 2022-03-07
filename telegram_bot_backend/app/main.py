import os

from fastapi import FastAPI,Request
import telegram 
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()


app=FastAPI()

bot = telegram.Bot(token=(os.getenv('ACCESS_TOKEN')))

@app.post('/hook')
async def webhook_handler(request:Request):
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        body = await request.json()
        update = telegram.Update.de_json(body, bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

def reply_handler(update:telegram.Update, context: CallbackContext):
    """Reply message."""
    text = update.message.text
    update.message.reply_text(text)

dispatcher = Dispatcher(bot, None)

dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))