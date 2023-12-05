from bark.generation import load_codec_model, generate_text_semantic
from encodec.utils import convert_audio

import torchaudio
import torch

import numpy as np
from argparse import ArgumentParser

def clone_voice(args):

    device = 'cpu' if args.disable_gpu else 'cuda'
    model = load_codec_model(use_gpu=True if device == 'cuda' else False)

    # From https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer
    from hubert.hubert_manager import HuBERTManager
    hubert_manager = HuBERTManager()
    hubert_manager.make_sure_hubert_installed()
    hubert_manager.make_sure_tokenizer_installed()

    # From https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer 
    # Load HuBERT for semantic tokens
    from hubert.pre_kmeans_hubert import CustomHubert
    from hubert.customtokenizer import CustomTokenizer

    # Load the HuBERT model
    hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)

    # Load the CustomTokenizer model
    tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)  # Automatically uses the right layers

    # Load and pre-process the audio waveform
    audio_filepath = args.seed # the pip uaudio you want to clone (under 13 seconds)
    wav, sr = torchaudio.load(audio_filepath)
    wav = convert_audio(wav, sr, model.sample_rate, model.channels)
    wav = wav.to(device)

    semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
    semantic_tokens = tokenizer.get_token(semantic_vectors)

    # Extract discrete codes from EnCodec
    with torch.no_grad():
        encoded_frames = model.encode(wav.unsqueeze(0))
    codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()  # [n_q, T]


    # move codes to cpu
    codes = codes.cpu().numpy()
    # move semantic tokens to cpu
    semantic_tokens = semantic_tokens.cpu().numpy()


    voice_name = args.voice_name # whatever you want the name of the voice to be
    output_path = 'bark/assets/prompts/' + voice_name + '.npz'
    np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)

def clone_several(names, seeds):
    device = 'cuda'
    model = load_codec_model(use_gpu=True if device == 'cuda' else False)

    # From https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer
    from hubert.hubert_manager import HuBERTManager
    hubert_manager = HuBERTManager()
    hubert_manager.make_sure_hubert_installed()
    hubert_manager.make_sure_tokenizer_installed()

    # From https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer 
    # Load HuBERT for semantic tokens
    from hubert.pre_kmeans_hubert import CustomHubert
    from hubert.customtokenizer import CustomTokenizer

    # Load the HuBERT model
    hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)

    # Load the CustomTokenizer model
    tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)  # Automatically uses the right layers
    for n, s in zip(names, seeds):
        # Load and pre-process the audio waveform
        audio_filepath = s # the pip uaudio you want to clone (under 13 seconds)
        wav, sr = torchaudio.load(audio_filepath)
        wav = convert_audio(wav, sr, model.sample_rate, model.channels)
        wav = wav.to(device)

        semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
        semantic_tokens = tokenizer.get_token(semantic_vectors)

        # Extract discrete codes from EnCodec
        with torch.no_grad():
            encoded_frames = model.encode(wav.unsqueeze(0))
        codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()  # [n_q, T]


        # move codes to cpu
        codes = codes.cpu().numpy()
        # move semantic tokens to cpu
        semantic_tokens = semantic_tokens.cpu().numpy()


        voice_name = n # whatever you want the name of the voice to be
        output_path = 'bark/assets/prompts/' + voice_name + '.npz'
        np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)



if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("voice_name", help="Name of voice")
    parser.add_argument("--seed", default = "seeds/scottish.wav", help="Seed audio")
    parser.add_argument("--disable_gpu", action="store_true", help="Shift to CPU compute")
    
    args = parser.parse_args()

    clone_voice(args)
    
