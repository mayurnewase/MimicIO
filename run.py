"""
server starts:
    load all models

user starts a bot:
    send welcome message

user writes a text:
    encode it
    feed to models
    create audio file
    send it to that user
    delete that audio file from server
"""
import os
import shutil
import json
from flask import Flask, request

from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters


import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

dispatcher = None
bot = None
application = Flask(__name__)

from flask import Flask
app = Flask(__name__)

BOT_TOKEN = "1054401279:AAESaTfz5nNuI6pgn3zbsDoSkj7LROSV0Ec"

def setup_bot(token):
    global bot
    bot = Bot(BOT_TOKEN)
    dispatcher = Dispatcher(bot, None, workers = 0)

    #register handlers
    start_handler = CommandHandler("start", handler_start)
    dispatcher.add_handler(start_handler)

    return dispatcher

def handler_start(update, context):
    #global bot
    print("START INVOKED")
    update.bot.send_message(chat_id = context.effective_chat.id, text = "got it buddy")

@app.route("/", methods = ["POST"])
def root_function():
    global bot
    msg = request.get_data()
    print("msg is ", msg)
    decoded_msg = Update.de_json(json.loads(msg), bot)
    print("decode msg is ", decoded_msg)

    dispatcher.process_update(decoded_msg)
    
    return json.dumps({"message" : "success", "statusCode" : 200})

if __name__ == "__main__":
    dispatcher = setup_bot(BOT_TOKEN)
    

    app.run(host = "0.0.0.0", port = "443", ssl_context=('certificates/public.pem', 'certificates/private.key'), debug=True)













































