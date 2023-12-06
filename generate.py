from bark.api import generate_audio
from transformers import BertTokenizer
from bark.generation import SAMPLE_RATE, preload_models, codec_decode, generate_coarse, generate_fine, generate_text_semantic
from IPython.display import Audio

from scipy.io.wavfile import write as write_wav


from argparse import ArgumentParser
import numpy as np
import sys
import time
import os

from onepass import Wellford


def create_audio(args):
    # Enter your prompt and speaker here
    text_prompt = args.prompt
    voice_name = args.voice 
    

    # # download and load all models
    # preload_models(
    #     text_use_gpu=True,
    #     text_use_small=False,
    #     coarse_use_gpu=True,
    #     coarse_use_small=False,
    #     fine_use_gpu=True,
    #     fine_use_small=False,
    #     codec_use_gpu=True,
    #     force_reload=False,
    #     path="/mnt/d/models"
    # )

    print("Loading models")
    preload_models(path="new_models/")


    for i in range(args.repititions):

        print("Generating")
        # simple generation
        


        if args.is_file:

            with open(text_prompt) as f:
                lines = f.readlines()
            
            for j in range(len(lines)):
                audio_array = generate_audio(lines[j], history_prompt=voice_name, text_temp=0.7, waveform_temp=0.7)
                filepath = f"{args.audio_name}_{i}_{j}.wav" # change this to your desired output path
                write_wav(filepath, SAMPLE_RATE, audio_array)
        else:
        # save audio
            audio_array = generate_audio(text_prompt, history_prompt=voice_name, text_temp=0.7, waveform_temp=0.7)
            filepath = f"{args.audio_name}_{i}.wav" # change this to your desired output path
            write_wav(filepath, SAMPLE_RATE, audio_array.astype(np.int16))


def generate_many_voices(prompt_file, voices, start_at = 0, repetitions = 5, skip = 1, target_directory = "skill_output/", models = "./models/"):

    print("Loading models")
    preload_models(path=models)
    print("Finished loading models")

    

    with open(prompt_file) as pf:

        next_prompt = pf.readline()
        count = 0

        while next_prompt != '':
            if count>=start_at:
                start = time.time()
                next_prompt = next_prompt[:-1]

                print(f"Generating prompt {next_prompt}")
                for i in range(repetitions):
                    times = {}
                    for v in voices:
                        times[v] = Wellford()

                    for v in voices:
                        start_time = time.time()
                        audio_array = generate_audio(next_prompt, history_prompt=v, text_temp=0.7, waveform_temp=0.7, silent=True)
                        filepath = f"{target_directory}{v}_{count}_{i}.wav"
                        write_wav(filepath, SAMPLE_RATE, audio_array)
                        times[v].sample(time.time() - start_time)
                    
                    s = ""
                    total = 0
                    for v in voices:
                        s += f"{v}: {times[v].get_x_bar():.2f} "
                        total += times[v].get_x_bar()

                    print(f"Average times per utterance - {s}. Remaining time for {next_prompt} - {total * (repetitions - i):.2f} seconds", end="\r")


                
                print(f"\n\nExecution took {time.time() - start} seconds\n\n")


            for _ in range(skip):
                next_prompt = pf.readline()
                count += 1  

            
def get_prompt_words(file):
    with open(file) as f:
        text = f.read()

    text = list(set(text.split()))

    with open("words.txt", "w") as w:

        for t in text:
            w.write(f"{t}\n")

    
if __name__ == "__main__":
    # parser = ArgumentParser()

    # parser.add_argument("--prompt", default="Hello, my name is Serpy. And, uh — and I like pizza. [laughs]", help="The text to speach string or file")
    # parser.add_argument("-f", "--is_file", action="store_true", help="prompt argument is the path to a file.")
    # parser.add_argument("--voice", default="output", help="Voice to use")
    # parser.add_argument("--audio_name", default="output/audio", help="File path and name of file. Do not include extentions.")
    # parser.add_argument("--repititions", type=int, default=5, help="Number of times to generate the sample.")

    # args = parser.parse_args()

    # create_audio(args)

    parser = ArgumentParser()
    parser.add_argument("promptFile",  help = "File with one prompt per line")
    parser.add_argument("voices", nargs = "+", help="List of voices to generate")
    parser.add_argument("--start_at", type = int, help = "Line number in prompt file to start at (starting with 0)", default=0)
    parser.add_argument("--repetitions", type = int, help = "Number of times to repeat each prompt for each voice.", default=5)
    parser.add_argument("--skip", type=int, default = 1, help = "Number of lines to iterate on each repetition. Default is 1.")
    parser.add_argument("--output_directory", default = "output/", help = "Directory to store results in.")
    parser.add_argument("--model_directory", default = "./models", help = "Location of predownloaded models")
    args = parser.parse_args()
    # pf = sys.argv[1]
    # voices = sys.argv[2:]

    #883 is where I increased the sample size
    last = 1226


    # get_prompt_words(pf)
    
    if not os.path.exists(args.output_directory):
        os.mkdir(args.output_directory)

    generate_many_voices(args.promptFile, args.voices, start_at = last, repetitions=50, skip=1, target_directory="words_output/", models = args.model_directory)



