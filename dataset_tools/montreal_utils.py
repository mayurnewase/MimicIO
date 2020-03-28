import pandas as pd
import librosa
import numpy as np
from pathlib import Path
from .convert import save_wav

def strip_audio_in_seconds(start, end):
    pass

def preprocess_montreal_aligner(audio_path, subs_path, output_path, sample_rate = None):
    """
    it needs .wav and .lab file with same name,and produces word based alignments
    
    input:
        audio file path of one wav file of one episode
        subtitle path of one episode
        output path to store all files

    process:
        take lines from subs file and put in same dir of wav with name line_number.lab in output path
        from that time info strip audio that part and store in output path with name line_number.wav

    output:
        how many successeded and failed
    """

    success = 0
    fail = 0

    #load audio file
    print("-----loading file--------")
    audio, sample_rate = librosa.load(audio_path, sr = sample_rate, mono = True)
    print("---------file loaded at sample rate of ", sample_rate)
    #load subtitle file
    sub_data = pd.read_csv(subs_path)

    #in loop from start and end seconds from sub file:
        #   strip from audio file and save it to output path
        #   also text and save to output path
    
    for start, end, line_number, label, annotation in zip(sub_data["start"], sub_data["end"],
                                                            sub_data["line_number"], sub_data["label"], sub_data["text"]):

        data = audio[int(start/1000 * sample_rate) : int(end / 1000 * sample_rate)]
        if not label or label == "nan" or label == np.nan or isinstance(label, float):
            fail += 1
            continue

        base_path = Path(output_path).joinpath(label)
        base_path.mkdir(exist_ok = True, parents = True)

        save_wav(np.array(data), base_path.joinpath(f"{label}-{line_number}.wav"), sample_rate)
        with open(base_path.joinpath(f"{label}-{line_number}.lab"), "w") as f:
            f.write(annotation)
        success += 1

    return success, fail
    


    






































