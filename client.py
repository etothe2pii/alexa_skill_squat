from alexa_client import AlexaClient
from alexa_client.alexa_client import constants
from alexa_client.alexa_client import helpers

import sys
import os
from datetime import datetime
import subprocess as sp
import time
import h2

from  loop_timer import Looper

from argparse import ArgumentParser

# client = AlexaClient(
#     client_id='amzn1.application-oa2-client.1ef94c1474bc43a58f4f699037173ce3',
#     secret="amzn1.oa2-cs.v1.5f73d27b79af4c59865a3adfc68499bdbfb17e3fc831ae962ba2babd0591527b",
#     refresh_token="Atzr|IwEBIEZzx-jLLwlMtXCmDZu845rpnxutVjHZj1e1I8sEaiDljATNKNHQYI4BKoan_VaBzLvgrnE-URTjPXnPwx2q7ZNLC43dAWH7tS3qqTgOhOPEg9zvA1G--U3XhCflTfHFAB7rEc4cje3Vq_AcwoxA1tWUyckStIwxjjEKnTNOaBAlsJappQZDVw3WSA9f-8tWZ9LCp_yFa9ZIitZuaeQmyF04_DBti1dX0EYOyAQLJ4utIB7y4woffNiOiCXlargDA2piTW75UbHEfH3-BAuJ7x41RtDXwQJ-HPzy1T0gcBVhgTyCWuqPIZCR8-DqLTKTJGWe7hrfvZLzkBuUGAQ-wPX3KGIlXSPnz-PIu-wHh2i2LjreIZNMb-UC9bXOrP8NPB8",
#     base_url= 'alexa.na.gateway.devices.a2z.com', 
# )

# print("Connecting")

# time = 'alexa_what_time_is_it.wav'
voice_pad = 'recordings_down/voice_pad.wav'
my_time = "recordings_down/time_new.wav"
record = "recordings_down/record.wav"
yes = "recordings_down/yes.wav"
stop = "recordings_down/stop.wav"
email = "recordings_down/email.wav"

repeat_me = "recordings_down/repeat_me.wav"
repeat_last = "recordings_down/repeat_what_I_said.wav"
exit_skill = "recordings_down/exit_skill.wav"

class Logger:

    def __init__(self):
        self.log_name = "logs/" + sys.argv[0].split(".")[0].split("/")[-1] + "_log _" + self.get_time() + ".txt"
        print(self.log_name)
        
        self.log_file = open(self.log_name, "w")

    def get_time(self):
        return datetime.now().strftime("%H_%M_%S")
    
    def log(self, message, to_stdout = False):
        m = f"{self.get_time()}:: {message}"
        self.log_file.write(m + "\n")

        if to_stdout:
            print(m)


    def close(self):
        self.log_file.close()
            




def record_session(client, audios):
    print("Generating id")
    dialog_request_id = helpers.generate_unique_id()

    for v in audios:
        print("Sending ...")
        directive_response = client.send_audio_file(open(v, "rb"), dialog_request_id=dialog_request_id)

        print(directive_response)

        if directive_response:

            for i, directive in enumerate(directive_response):
                print(i, directive)
                if directive.name in ['Speak', 'Play']:
                    with open(f'responses/output_{v.split(".")[0].split("/")[-1]}_{i}.mp3', 'wb') as f:
                        print("writing to file ...")
                        f.write(directive.audio_attachment)
        else:
            print("Directive was None")




'''
====================================
            Main Test
====================================
'''

def run_test(client, directory, logger, output):

    global output_dir
    output_dir = output

    
    p = sp.Popen(f"convert_audio/convert_to_mono.sh {directory} converted_audio/", shell=True)
    p.communicate()
    files = os.listdir("converted_audio")
    while True:
        logger.log(f"In run_test:: Opened {directory}. {len(files)} files available.", to_stdout = True)
        counter = 1
        for f in Looper(files):
            
            f = f"converted_audio/{f}"
            logger.log(f"In run_test:: Running test on {f}. {counter}/{len(files)}: {counter/len(files)*100:.2f}% finished with this cycle", to_stdout = False)
            dialog_request_id = helpers.generate_unique_id()
            logger.log(f"In run_test:: unique dialog id: {dialog_request_id}")


            send_test_audio(client, f, dialog_request_id, logger)
            send_exit(client, dialog_request_id, logger)
            send_repeat(client, f, dialog_request_id, logger)

            logger.log(f"In run_test:: Moving {f} to used_audio")
            os.rename(f,  f"used_samples/{f.split('/')[-1]}")
            counter += 1

        p = sp.Popen(f"convert_audio/convert_to_mono.sh {directory} converted_audio/", shell=True)
        p.communicate()
        files = os.listdir("converted_audio")

        time.sleep(10)




def send_test_audio(client, audio_file, id, logger):
    logger.log(f"In send_test_audio:: Sending {audio_file} to AVS server . . .")
    response = client.send_audio_file(open(audio_file, "rb"), dialog_request_id=id)

    #parse_response(response, f"word_response/{audio_file.split('/')[-1].split('.')[0]}.mp3", logger)

def send_exit(client, id, logger):
    logger.log(f"In send_exit:: Sending exit skill to AVS server . . .")
    response = client.send_audio_file(open(exit_skill, "rb"), dialog_request_id=id)

    #parse_response(response, f"word_response/exit_skill.mp3", logger)

def send_repeat(client, audio_file, id, logger):
    logger.log(f"In send_repeat::  Sending exit skill to AVS server . . .")
    response = client.send_audio_file(open(repeat_last, "rb"), dialog_request_id=id)

    parse_response(response, f"{output_dir}/{audio_file.split('/')[-1].split('.')[0]}.mp3", logger)


def parse_response(response, file_location, logger):
    if response:
        for i, directive in enumerate(response):
            if directive.name in ['Speak', 'Play']:
                with open(file_location, 'wb') as f:
                    logger.log(f"In parse_response:: Saving {file_location}")
                    f.write(directive.audio_attachment)
        return 0
    else:
        logger.log("In parse_response:: None response")
        return 1
    

    # print("Sending 1")
    # directives_one = client.send_audio_file(open(voice_pad, "rb"), dialog_request_id=dialog_request_id)
    # print("Sending 2")
    # directives_two = client.send_audio_file(open(record, "rb"), dialog_request_id=dialog_request_id)
    # print("Sending 3")
    # directives_three = client.send_audio_file(open(audio, "rb"), dialog_request_id=dialog_request_id)
    # print("Sending 4")
    # directives_four = client.send_audio_file(open(stop, "rb"), dialog_request_id=dialog_request_id)
    # print("Sending 5")
    # directives_five = client.send_audio_file(open(email, "rb"), dialog_request_id=dialog_request_id)
    # print("Sending 6")
    # directives_six = client.send_audio_file(open(yes, "rb"), dialog_request_id=dialog_request_id)
    # print("Done")

# client.connect()  # authenticate and other handshaking steps
# print("Connected")
# with open(voice_pad, 'rb') as f:
#     # print("Open file stream")
#     # print(f)
#     a = client.send_audio_file(f)
#     print("a", a)
#     for i, directive in enumerate(a):
#         print(i, directive)
#         if directive.name in ['Speak', 'Play']:
#             with open(f'./output_{i}.mp3', 'wb') as f:
#                 print("writing to file ...")
#                 f.write(directive.audio_attachment)

if __name__ == "__main__":
    client = AlexaClient(
        client_id='amzn1.application-oa2-client.1ef94c1474bc43a58f4f699037173ce3',
        secret="amzn1.oa2-cs.v1.5f73d27b79af4c59865a3adfc68499bdbfb17e3fc831ae962ba2babd0591527b",
        refresh_token="Atzr|IwEBIEAISagQ7r-rO2Rcaa_02-Qo53ApG7svKJVGD4CRNwGKhbcEi92nl12yy3Nxqsb6ycrMWyiInTfiNB-OScAoulqUALp_A-S-0ioGqNurXri4wcHleItBfqLMkYxuQ_696wp4Mu16xsBziwYqUKgVUSgOpc_9Iby43Y463tDqh2SsSpNTK2AYdxwER3oBzQ3wK6wz362jaPEnwc9C660wulIW9cy_oL-hXZ2nnBoWRIOXOLuJOMTJQ4i-A7cASa-KOQHotAHQqJZWDC9GhZmNPcLBcujCnaMdmNa9U-BTTB9hXsTenGw5Wb1cwf4bGQmCxqun0azzm5pSUTKMPpOw80u2FBvSVvII2_D7lEy2T7MnxWX1WJiOe4qayv0qCJ16nKU",
        base_url= 'alexa.na.gateway.devices.a2z.com', 
    )

    parser = ArgumentParser()

    parser.add_argument("input_directory", help = "Audio Samples for transcription.")
    parser.add_argument("output_directory", help = "Alexa samples")

    

    args = parser.parse_args()

    if not os.path.exists(args.output_directory):
        os.mkdir(args.output_directory)

    l = Logger()

    l.log(f"In main:: Connecting", to_stdout = True)
    client.connect()
    l.log(f"In main:: Connected", to_stdout = True)



    skill_audio = "../bark-with-voice-clone/skill_output/"
    word_audio = "../bark-with-voice-clone/words_output/"


    # try:
    run_test(client, args.input_directory, l, args.output_directory)
    # except Exception as e:
    #     print(e)
    #     print("Restarting . . .")
    #     time.sleep(5)
    #     sp.Popen(".venv/bin/python3 client.py", shell = True)
    #     sys.exit(1)
    # print("Connecting")

    # client.connect()

    # print("Connected")

    # sequence = [voice_pad, record, "recordings_down/test.wav", stop, email, yes]
    # s2 = ["recordings_down/test.wav", repeat_last]
    # s3 = [voice_pad, exit_skill, repeat_last]
    # record_session(client, s3)
    

