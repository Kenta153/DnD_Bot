import threading
import io
import numpy as np
from discord.player import AudioSource
import os
from utils.voice import load_model, load_latents, float2pcm
import asyncio
from discord.opus import Encoder as OpusEncoder
import json

class SpeechSource(AudioSource):

    def __init__(self):
        self.lock = threading.Lock()
        self.stream = io.BytesIO()
        self.killed = False

    async def wait_until_stream_is_not_empty(self):
        while True:
            with self.lock:
                byte_len = len(self.stream.getbuffer())
            if byte_len > 0:
                break
            await asyncio.sleep(0.1)

    def write(self, data):
        with self.lock:
            position = self.stream.tell()
            self.stream.seek(0, 2)
            self.stream.write(data)
            self.stream.seek(position)

    def read(self):
        with self.lock:
            ret = self.stream.read(OpusEncoder.FRAME_SIZE)
            if len(ret) != OpusEncoder.FRAME_SIZE or self.killed:
                return b""
            return ret
        

class Speech:
    voice_model = load_model(os.path.join(os.getcwd(), "checkpoint"))
    gpt_cond_latent, speaker_embedding = load_latents(os.path.join(os.getcwd(), "checkpoint\\latents.json"))
    source = SpeechSource()
    inference_stream = None
    inference_flag = 0

    @classmethod
    def new_voice(cls, voice_path):
        cls.gpt_cond_latent, cls.speaker_embedding = cls.voice_model.get_conditioning_latents(audio_path=voice_path)

        latents = {
            "gpt_cond_latent": cls.gpt_cond_latent.cpu().squeeze().half().tolist(),
            "speaker_embedding": cls.speaker_embedding.cpu().squeeze().half().tolist(),
        }

        with open(os.path.join(os.getcwd(), "checkpoint\\latents.json"), "w") as new_file:
            json.dump(latents, new_file)

    @classmethod
    def inference(cls, text):
        for sentence in text:
            chunks = cls.voice_model.inference_stream(
                sentence, "ru", cls.gpt_cond_latent, cls.speaker_embedding
            )
            for chunk in chunks:
                if cls.inference_flag == 1:
                    print("Killing inference!")
                    cls.inference_flag = 0
                    return
                cls.source.write(np.repeat(float2pcm(chunk), 4))

    @classmethod
    async def process(cls, text):

        #killing inference
        await cls.kill()

        #reseting stream
        cls.source.killed = True
        cls.source = SpeechSource()

        #creating inference stream
        cls.inference_stream = threading.Thread(target=cls.inference, args=(text,))
        cls.inference_stream.start()

        await cls.source.wait_until_stream_is_not_empty()
        return cls.source
    
    @classmethod
    async def kill(cls):

        while cls.inference_flag:
            await asyncio.sleep(0.1)

        if cls.inference_stream:
            cls.inference_flag = 1
            while cls.inference_flag and cls.inference_stream.is_alive():
                await asyncio.sleep(0.1)
            cls.inference_flag = 0