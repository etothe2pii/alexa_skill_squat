# Alexa Skill Squatting Voice Clone

Hey! This is a final project for an IOT Security course. I thought it would be fun to extend the paper [Skill Squatting Attacks on Amazon Alexa](https://www.usenix.org/conference/usenixsecurity18/presentation/kumar) by using tts to target the specific invocation words that are used in the AVS ecosystem. Since I have to turn in this code, here's the instructions on how to run it, since it's not super straight forward. I've tried to simplify it as much as I possibly can, but good luck anyways!

## Setup

First clone this repo.

```
git clone https://github.com/etothe2pii/alexa_skill_squat.git
```

Then, cd into the directory and install the requirements:

```
pip install -r requirements.txt
```

## Starting the framework

### Voices

First you need your voices. Find a 5-12 second clip of audio of whatever accents you want. Some good tips on this are [here](https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer). Once you have that, you can use clone.py to create the voice. For demonstration purposes, I used a southern accent for my project.

```
python3 clone.py southern southern.wav
```

Which will generate a `southern.npz` file.

### Generating Audio

This is the most time consuming part of the whole thing, at least for my computer. If you have a lot of compute available, the bottleneck may be the AVS client. 