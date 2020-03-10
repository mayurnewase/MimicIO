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
from flask import Flask

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

arguments = None
parameters = None
predictor = None
audio_adapter = None
application = Flask(__name__)

BOT_TOKEN = "1030183690:AAEawegpjKXjvmPl2KyFAPrynDuE8rFT0xc"

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(ssl_context='adhoc')












































