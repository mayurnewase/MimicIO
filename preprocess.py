from dataset_tools.convert import convert_to_wav, isolate_voice, isolate_text
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(
        description = "preprocess files"
    )

def main():
    parser.add_argument("--process", type = str, help = "convert/isolate")
    parser.add_argument("--input_path", type = Path, required = True, help = "path to specific season")
    parser.add_argument("--output_path", type = Path, required = True, help = "path to output processed files")
    parser.add_argument("--params_path", type = Path, required = True, help = "path to params file")
    parser.add_argument("--embeds_path", type = Path, required = True, help = "path to speaker embeds file")
    parser.add_argument("--sub_path", type = Path, required=False, help = "path to input subtitle file to get script")
    parser.add_argument("--sync", type = str, required=False, default=None, help = "sync for sub/video in seconds like +2.8")
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

if __name__ == "__main__":
    main()