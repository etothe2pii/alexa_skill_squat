import whisper
import os
import time
from datetime import datetime

from argparse import ArgumentParser

def get_time():
    return datetime.now().strftime("%H_%M_%S")


def parse_file(model, audio_file, output_directory):

    #print(f"{get_time()}:: In parse_file:: transcribing {audio_file}")
    result = model.transcribe(audio_file)


    file_name = audio_file.split("/")[-1].split(".")[0] + ".txt"


    with open(f"{output_directory}{file_name}", "w") as f:
        
        f.write(result["text"])

def extract_text(directory, output_directory):

    print(f"{get_time()}:: extract_text:: Loading model")
    model = whisper.load_model("base")
    print(f"{get_time()}:: extract_text:: Model loaded")
    
    files = os.listdir(directory)
    count = 0
    while True:

        files = os.listdir(directory)

        if len(files) > 0:
            print(f"{get_time()}:: extract_text:: {count} files complete out of {len(files) + count}. {count/(len(files) + count)*100:.2f}% done.")
            f = files.pop(0)
            f_path = f"{directory}{f}"
            parse_file(model, f_path, output_directory)
            os.rename(f_path, f"used_alexa/{f}")

            count += 1
        
        else:
            time.sleep(5)



if __name__ == "__main__":


    parser = ArgumentParser()

    parser.add_argument("input_directory", help = "Audio Samples for transcription.")
    parser.add_argument("output_directory", help = "Alexa samples")

    

    args = parser.parse_args()


    if not os.path.exists(args.output_directory):
        os.mkdir(args.output_directory)

    extract_text(args.input_directory, args.output_directory)



