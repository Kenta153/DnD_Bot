from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import os
import json
import torch
import numpy as np

def load_model(path):
    config = XttsConfig()
    config.load_json(os.path.join(path, "config.json"))

    voice_model = Xtts.init_from_config(config)
    voice_model.load_checkpoint(config, checkpoint_dir=path)
    voice_model.cuda()

    return voice_model

def load_latents(path):
    with open(path, "r") as new_file:
        latents = json.load(new_file)

        speaker_embedding = (torch.tensor(latents["speaker_embedding"]).unsqueeze(0).unsqueeze(-1))
        gpt_cond_latent = (torch.tensor(latents["gpt_cond_latent"]).reshape((-1, 1024)).unsqueeze(0))

        return gpt_cond_latent, speaker_embedding   
    
def float2pcm(sig, dtype='int16'):
    sig = sig.detach().cpu().numpy()
    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)