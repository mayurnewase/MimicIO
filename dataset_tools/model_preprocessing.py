import pandas as pd
import librosa
import numpy as np
from pathlib import Path
from .convert import save_wav

"""
input:
    aligned directory root which contains:
        R:
            R-1.textgrid
            R-2.textgrid
            R-3.textgrid
        M:
            M-1.textgrid
            M-1.textgrid
            M-1.textgrid
output:
    in rick_and_morty training data:
        R:
            R-1.alignment.txt of format:
                R-1
                ",hey,morty," "0.54, 0.90"

            all flac files
        M:
            M-1.alignment.txt
            all flac files

How:
    from input dir:
        read all textgrid file names
    
    open one output file in output dir with name R.alignment.txt

    for each file of textgrid [R-1, R-2, R-3]:
            open in read mode
            in item -> item[1] text and xmax from intevals [1,2,3,...]
            write to open output file in following format:
                R-1
                ",text-1,text-2," "time-1,time-2"
                R-2
                ",text-1,text-2," "time-1,time-2"
"""
def find_text_and_interval(file_path):
    
    data =  open(file_path, mode="r").read()
    data = data.split("\n")
    for index in range(len(data)):
        data[index] = data[index].strip()
    
    all_text = []
    all_intervals = []

    for index in range(len(data)):
        line = data[index]
        line = line.strip()

        if line == 'name = "words"':
            interval_index = index + 3
            size = int(data[interval_index].split(" ")[-1])

            while size > 0:
                if data[interval_index].startswith("xmax"):
                    all_intervals.append(data[interval_index].split(" ")[-1])

                elif data[interval_index].startswith("text"):
                    print(data[interval_index])
                    all_text.append(data[interval_index].split(" ")[-1].replace('"', ""))
                    size -= 1
            
                interval_index += 1
            break

    return all_text, all_intervals
            
def preprocess_training_data(input_path, output_path):
    #read all textgrid files
    all_files = list(input_path.glob("*.TextGrid"))
    #print("all files ", all_files)

    #open one output file with name of R.alignment.txt in output path
    output_file = open(output_path.joinpath("R.alignment.txt"), mode = "w")

    for input_textgrid_file in all_files:
        text, intervals = find_text_and_interval(input_textgrid_file)
        print("text and interval ", text, intervals)
        
        output_file.write(input_textgrid_file.stem)
        
        output_file.write("\n")

        output_file.write("\"")
        
        text_string = ""
        for index in range(len(text)):
            t = text[index]
            text_string += t if t != '""' else ""
            if index != len(text) - 1:
                text_string += ","

        output_file.write(str(text_string))

        output_file.write("\" ")
        
        output_file.write("\"")

        for index in range(len(intervals)):
            i = intervals[index]
            output_file.write(i if i != '"' else "")
            if index != len(intervals) - 1:
                output_file.write(",")

        output_file.write("\"")

        output_file.write("\n")






























