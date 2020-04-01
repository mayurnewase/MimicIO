from dataset_tools.convert import convert_to_wav, isolate_voice, isolate_text
from dataset_tools.montreal_utils import preprocess_montreal_aligner
from dataset_tools.model_preprocessing import preprocess_training_data

from pathlib import Path
import argparse

parser = argparse.ArgumentParser(
        description = "preprocess files"
    )

def main():
    parser.add_argument("--process", type = str, help = "convert/isolate")
    parser.add_argument("--input_path", type = Path, required = True, help = "path to specific season's audio files")
    parser.add_argument("--output_path", type = Path, required = True, help = "path to output processed files")
    parser.add_argument("--params_path", type = Path, required = False, help = "path to params file")
    parser.add_argument("--embeds_path", type = Path, required = False, help = "path to speaker embeds file")
    parser.add_argument("--sub_path", type = Path, required=False, help = "path to input subtitle file to get script")
    parser.add_argument("--sync", type = str, required=False, default=None, help = "sync for sub/video in seconds like +2.8")
    parser.add_argument("--sr", type = int, required=False, default=None, help="sample rate for montreal preprocessing")

    args = parser.parse_args()

    if args.process == "convert":
        convert_to_wav(args.input_path, args.output_path, args.params_path)

    elif args.process == "isolate":
        rick_seconds, morty_seconds = isolate_voice(args.input_path, 
                                                    args.embeds_path,
                                                    args.params_path,
                                                    args.output_path)

        rick_text, morty_text = isolate_text(rick_seconds, morty_seconds, args.sub_path, args.output_path, args.sync)
        
        print("final seconds ", rick_seconds, "\n\n", morty_seconds)
        print("\nfinal text \n", rick_text, "\n\n", morty_text)

    elif args.process == "preprocess_montreal":
        result = preprocess_montreal_aligner(args.input_path, args.sub_path, args.output_path, args.sr)

    elif args.process == "preprocess_training_data":
        #convert textgrid for training model
        result = preprocess_training_data(args.input_path, args.output_path)
        #python3 preprocess.py --process=preprocess_training_data --input_path="/home/mayur/projects/datasets/rick_morty_aligned/R" --output_path="/home/mayur/projects/datasets/rick_morty_training_data"

if __name__ == "__main__":
    main()