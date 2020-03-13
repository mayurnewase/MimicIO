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

from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import librosa
import pickle

import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

dispatcher = None
bot = None

application = Flask(__name__)

from flask import Flask
app = Flask(__name__)

BOT_TOKEN = "1054401279:AAESaTfz5nNuI6pgn3zbsDoSkj7LROSV0Ec"

#encoder_path = "/home/mayur/projects/Real-Time-Voice-Cloning/encoder/saved_models/pretrained.pt"
synthesizer_path = "/home/mayur/projects/Real-Time-Voice-Cloning/synthesizer/saved_models/logs-pretrained/taco_pretrained"
vocoder_path = "/home/mayur/projects/Real-Time-Voice-Cloning/vocoder/saved_models/pretrained/pretrained.pt"
embedding_path = "/home/mayur/projects/Resemblyzer/audio_data/rick_90_morty_50.pkl"
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
    dispatcher = Dispatcher(bot, None, workers = 0)

    #register handlers
    start_handler = CommandHandler("start", start_callback)
    text_handler = MessageHandler(Filters.text, text_callback)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(text_handler)

    embedding = load_embed()
    encoder, synthesizer, vocoder = load_models()

    return dispatcher

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

@app.route("/", methods = ["POST"])
def root_function():
    global bot
    msg = request.get_json()
    print("msg is ", msg)
    decoded_msg = Update.de_json(msg, bot)

    dispatcher.process_update(decoded_msg)

    return json.dumps({"message" : "success", "statusCode" : 200})

if __name__ == "__main__":
    dispatcher = setup_bot(BOT_TOKEN)
    app.run(host = "0.0.0.0", ssl_context=('certificates/public.pem', 'certificates/private.key'), debug=True)
















