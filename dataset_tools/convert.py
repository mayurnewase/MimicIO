from resemblyzer import preprocess_wav, VoiceEncoder
from pathlib import Path
import subprocess
import json
import pickle
import numpy as np
import pandas as pd
import librosa
import re
import datetime
import operator

def list_all_files(path: Path, pattern):
    return list(path.glob(pattern))

def check_file_exists(filename, out_path: Path):
    if out_path.joinpath(filename).exists():
        print(out_path.joinpath(filename))
        print("true")
        return True
    return False

def get_filename_from_path(file_path: Path):
    return file_path.name.split(' ')[-1].split(".")[0]

def mkv_to_wav(mkv_file_path, out_dir: Path, convert_params):
    file_name = get_filename_from_path(mkv_file_path)
    out_dir.mkdir(exist_ok=True)
    command = f"ffmpeg -i '{mkv_file_path}' -ar {convert_params['wav_bitrate']} -vn {out_dir}/{file_name}.wav"
    result = subprocess.Popen(command, stdout = subprocess.PIPE, shell=True).communicate()

def load_params(params_path):
    return json.load(open(params_path, "r"))

def convert_to_wav(input_path: Path, output_path: Path, params_path: Path):
    """
    check if out_file already exists -> if yes skip
    if not than convert to wav
    #save in out_dir with same filename
    """
    all_files = list_all_files(input_path, "*.mkv")
    convert_params = load_params(params_path)
    for file_path in all_files:
        
        file_name = get_filename_from_path(file_path)
        if not check_file_exists(file_name, output_path):
            print("doing it")
            _ = mkv_to_wav(file_path, output_path, convert_params)

def save_wav(array, path, sampling_rate):
    print("saving in ", path)
    dir_path = path.parents[0]
    dir_path.mkdir(exist_ok = True, parents = True)
    librosa.output.write_wav(path, array.astype(np.float32), sr = sampling_rate)

def isolate_voice(audio_file_path: Path, embed_path: Path, params_path: Path, output_path: Path):
    """
    load speaker embeds from pickle
    take voice out only if value is > thresh and take greater if both > thresh
    
    Args:
        file_path: input complete wav file path from which rick's voice will be taken out
        cutoff_thresh: voice if value above this is taken
    """
    params = load_params(params_path)
    cutoff_threshold = params["cutoff_threshold"]
    sampling_rate = params["wav_bitrate"]

    print("preprocessing")
    file_wav = preprocess_wav(audio_file_path) ; print("input file shape ", file_wav.shape, "\n", file_wav[:10])
    print("file preprocessed")
    encoder = VoiceEncoder("cpu")
    print("model loaded")
    speaker_names = ["Rick", "Morty"]

    _, file_embeds, wav_splits = encoder.embed_utterance(file_wav, return_partials=True, rate=1)
    print("file encoded")
    speaker_embeds = pickle.load(open(embed_path, "rb"))

    similarity_dict = {name: file_embeds @ speaker_embed for name, speaker_embed in zip(speaker_names, speaker_embeds)}
    print("similatrity dict is\n", similarity_dict)
    pickle.dump(similarity_dict, open("./similarity.pkl", "wb"))

    #find greater in both then cutoff -> take that second append it to that file
    current_second = 0
    rick_wav = []
    rick_seconds = []
    morty_wav = []
    morty_seconds = []

    for rick_value, morty_value in zip(similarity_dict["Rick"], similarity_dict["Morty"]):
        print(current_second, rick_value, morty_value)
        if rick_value > morty_value and rick_value > cutoff_threshold:
            rick_wav.append(file_wav[current_second * sampling_rate : (current_second+1) * sampling_rate])
            rick_seconds.append(current_second)
            print("append rick")

        elif morty_value > rick_value and morty_value > cutoff_threshold:
            morty_wav.append(file_wav[current_second * sampling_rate: (current_second+1) * sampling_rate])
            morty_seconds.append(current_second)
            print("append morty")

        else:
            print("skipping")

        current_second += 1

    rick_wav = [item for sublist in rick_wav for item in sublist]
    morty_wav = [item for sublist in morty_wav for item in sublist]
    
    save_wav(np.array(rick_wav), output_path.joinpath("rick.wav"), sampling_rate)
    save_wav(np.array(morty_wav), output_path.joinpath("morty.wav"), sampling_rate)

    return rick_seconds, morty_seconds

def get_milliseconds(datetime_obj: datetime.datetime):
    return datetime_obj.hour*60*60*1000 + datetime_obj.minute*60*1000 + datetime_obj.second*1000 + datetime_obj.microsecond/1000

def convert_text_to_df(subtitle_path):
    sub_file = open(subtitle_path, "r")
    
    line_number_regex = "^\d+$"
    time_regex = "^\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+$"
    text_regex = "^\w+"

    txt = sub_file.readlines()
    lines_df = pd.DataFrame(columns = ["line_number", "start", "end", "text"])
    line_dict = {}

    for line in txt[:]:
        #print("line is ", line)
        line = re.sub("\n", "", line)

        #if it matches regex then append to csv like it
        line_match = re.match(line_number_regex, line)
        if line_match:
            #line = re.sub("\n", "", line)
            line_dict["line_number"] = int(line)
            #print("line number hit")
            
            continue
        
        time_match = re.match(time_regex, line)
        if time_match:
            print("line", line)
            start, end = line.split(" --> ")
            start = get_milliseconds(datetime.datetime.strptime(start, "%H:%M:%S,%f"))
            end = get_milliseconds(datetime.datetime.strptime(end, "%H:%M:%S,%f"))

            line_dict["start"], line_dict["end"] = int(start), int(end)
            #print("time hit")
            continue

        text_match = re.match(text_regex, line)
        if text_match:
            line_dict["text"] = line
            #check if line number already exist in df -> if yes -> then append text to it
            
            if int(line_dict["line_number"]) in lines_df["line_number"].values:
                print("duplucate found", line_dict["line_number"])
                old_text = lines_df[lines_df["line_number"] == line_dict["line_number"]]["text"].values[0]
                
                full_text = f"{old_text} {line}"

                #print("old text ", old_text)
                #print("new text ", full_text)

                lines_df.loc[lines_df["line_number"] == line_dict["line_number"], "text"] = full_text

            else:
                lines_df = lines_df.append(line_dict, ignore_index = True)
                continue
    lines_df.to_csv("./processed.csv")
    return lines_df

def find_line_from_second(second: int, sync: str, sub_df: pd.DataFrame):
    """
    find second in that range (start inclusive, end exclusive)
    only from start it should be greater than one and less than next
    then take that first line
    TODO: use binary search to fnd right slot
    """

    line = sub_df[(second >= sub_df["start"]) & (second < sub_df["end"])]
    text = line["text"]
    #print("isolated text \n", text["start"], text["end"])
    return text.values[0] if len(text.values == 1) else None

def isolate_text(rick_seconds: list, morty_seconds: list, subtitle_path: Path, output_path: Path, sync: str = None):
    """
    take seconds
    from subs from initial from every line, find where that second belong
    then take that line and store in dict with that second as key
    """
    df = convert_text_to_df(subtitle_path)
    print("df is ",df)
    rick_text = {}
    morty_text = {}

    if sync:
        sync_ops = {"+" : operator.add, "-": operator.sub}
        sync_op, sync_duration = sync[0], float(sync[1:]) * 1000
    
    for second in rick_seconds:
        second = second * 1000
        if sync:
            second = sync_ops[sync_op](second, sync_duration)

        text = find_line_from_second(second, sync, df)
        rick_text[str(second)] = text

    for second in morty_seconds:
        second = second * 1000
        second = sync_ops[sync_op](second, sync_duration)

        text = find_line_from_second(second, sync, df)
        morty_text[str(second)] = text

    return rick_text, morty_text






























