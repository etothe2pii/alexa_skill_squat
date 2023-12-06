# Alexa Skill Squatting Voice Clone

Hey! This is a final project for an IOT Security course. I thought it would be fun to extend the paper [Skill Squatting Attacks on Amazon Alexa](https://www.usenix.org/conference/usenixsecurity18/presentation/kumar) by using tts to target the specific invocation words that are used in the AVS ecosystem. Since I have to turn in this code, here's the instructions on how to run it, since it's not super straight forward. I've tried to simplify it as much as I possibly can, but good luck anyways!

Note: There are a bunch of empty directories here. These are important, I promise. A lot of the scripts shuffle around the audio once they finish so that they can keep running without needing human interaction and without losing their place. I could make the code make them, but I'm being lazy.

## Setup

First clone this repo.

```
git clone https://github.com/etothe2pii/alexa_skill_squat.git
```

Then, cd into the directory and install the requirements:

```
pip install -r requirements.txt
```

Unfortunately, there's some weirdness with the bark ai pip install, so we need to install int manually.

```
git clone https://github.com/serp-ai/bark-with-voice-clone.git
pip install bark-with-voice-clone/
```

Additionally, install ffmpeg:

```
sudo apt install ffmpeg
```

I'm not sure if the AVS framework will work with the existing device I have registered. If it doesn't, you'll have to follow the steps in setup_device.md.

## Starting the framework

### Voices

First you need your voices. Find a 5-12 second clip of audio of whatever accents you want. Some good tips on this are [here](https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer). Once you have that, you can use clone.py to create the voice. For demonstration purposes, I used a southern accent for my project.

```
python3 clone.py southern southern.wav
```

Which will generate a `southern.npz` file.

### Generating Audio

This is the most time consuming part of the whole thing, at least for my computer. If you have a lot of compute available, the bottleneck may be the AVS client. We can do this using the generate.py script. This, for example, is using a single southern accent. We can pass any number of voices to the generate.py script for it to generate samples.

```
python3 generate.py words.txt southern
```

**WARNING:** This script will download large weight files to your computer. These are > 10 GB in total.

This will run until you run out of prompts in the prompt file.

### AVS Client

If you had to setup your new device, please edit client.py so that the client_id, secret, and refresh_token fields match the ones for your device. Then, you can run the service:

```
python3 client.py samples/ alexa_responses/
```

Quick note, this will likely periodically crash. I had to eventually write a script that opened client.py as a subprocess and restarted it when it errored.

### Whisper transcription

This should be fairly simple, just run the parse_audio.py script.

```
python3 parse_audio.py alexa_responses/ raw_text/
```

### Analysis

Feel free to analyze the data any way you would like. I found that the code in get_transcription.py was fairly informative, but by all means feel free to analyze the data you collect in other ways!

```
python3 get_transcription.py 
```
