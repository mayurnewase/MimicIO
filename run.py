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

use threading for updater -> done
make it git clone or docker container -> with secrets of bot_token, certificates
push it to ecr if required
use spot instances and fleet for atleast one alive with elastic ip

use wsgi with multiprocess model
add status endpoint to show system health
add track endpoint to check status of current task -> queued, failed, success, uploading
"""

import os
import shutil
import json
from flask import Flask, request

from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from queue import Queue
from threading import Thread

from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import librosa
import pickle

import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

dispatcher_update_queue = None
bot = None

application = Flask(__name__)

from flask import Flask
app = Flask(__name__)

BOT_TOKEN = "1054401279:AAESaTfz5nNuI6pgn3zbsDoSkj7LROSV0Ec"

#encoder_path = "/home/mayur/projects/Real-Time-Voice-Cloning/encoder/saved_models/pretrained.pt"
synthesizer_path = "./synthesizer/saved_models/logs-pretrained/taco_pretrained"
vocoder_path = "./vocoder/saved_models/pretrained/pretrained.pt"
embedding_path = "./rick_90_morty_30.pkl"
output_path = "./"

def load_embed():    
    embedding = pickle.load(open(embedding_path, "rb"))
    
    #take only ricks embedding
    embedding = embedding[0]
    return embedding

def load_models():
    #encoder_weights = Path(encoder_path)
    vocoder_weights = Path(vocoder_path)
    syn_dir = Path(synthesizer_path)
    #encoder.load_model(encoder_weights)
    synthesizer = Synthesizer(syn_dir)
    vocoder.load_model(vocoder_weights)

    return encoder, synthesizer, vocoder

def setup_bot(token):
    global bot
    global embedding
    global encoder, synthesizer, vocoder

    bot = Bot(BOT_TOKEN)
    update_queue = Queue()

    dispatcher = Dispatcher(bot, update_queue, workers = 1)

    #register handlers
    start_handler = CommandHandler("start", start_callback)
    text_handler = MessageHandler(Filters.text, text_callback)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(text_handler)

    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    embedding = load_embed()
    encoder, synthesizer, vocoder = load_models()

    return update_queue

def start_callback(bot, update):
    bot.send_message(chat_id = update.effective_chat.id, text = "yo")

def text_callback(bot, update):
    #global embedding
    #give to models
    print("\n\n\n\n update is ", update)
    print("\n\n\n\n bot is ", bot)
    spectrogram = synthesizer.synthesize_spectrograms([update.message.text], [embedding])
    wav = vocoder.infer_waveform(spectrogram[0])
    wav = np.pad(wav, (0, synthesizer.sample_rate), mode = "constant")
    print("\n\n\n====================final wav shape ", wav.shape)
    librosa.output.write_wav(f"{output_path}{update.effective_chat.id}.wav", wav, sr = synthesizer.sample_rate)
    bot.send_voice(chat_id = update.effective_chat.id, voice = open(f"{output_path}{update.effective_chat.id}.wav", "rb"), timeout = 100)

@app.route("/", methods = ["POST"])
def root_function():
    global bot
    msg = request.get_json()
    print("msg is ", msg)
    decoded_msg = Update.de_json(msg, bot)

    dispatcher_update_queue.put(decoded_msg)

    return json.dumps({"message" : "success", "statusCode" : 200})

if __name__ == "__main__":
    dispatcher_update_queue = setup_bot(BOT_TOKEN)
    app.run(host = "0.0.0.0", ssl_context=('certificates/public.pem', 'certificates/private.key'), debug=True)
















