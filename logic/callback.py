import time
import numpy as np
from discord.sinks.core import RawData
from discord.player import AudioSource
from discord.opus import Encoder as OpusEncoder
import threading
import io
from faster_whisper import WhisperModel
from openai import OpenAI
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import numpy as np
import asyncio

print("Loading model...")
config = XttsConfig()
config.load_json("c:\\Users\\Тимур\\AppData\\Local\\tts\\tts_models--multilingual--multi-dataset--xtts_v2\\config.json")
voice_model = Xtts.init_from_config(config)
voice_model.load_checkpoint(config, checkpoint_dir="C:\\Users\\Тимур\\AppData\\Local\\tts\\tts_models--multilingual--multi-dataset--xtts_v2\\", use_deepspeed=False)
voice_model.cuda()

gpt_cond_latent, speaker_embedding = voice_model.get_conditioning_latents(audio_path="DnD.wav")

latents = {
    "gpt_cond_latent": gpt_cond_latent.cpu().squeeze().half().tolist(),
    "speaker_embedding": speaker_embedding.cpu().squeeze().half().tolist(),
}


import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# # Настройка модели транскрипции
model_size = "large-v3"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

class Chat:
    def __init__(self, system_prompt: str = ""):
        self.client = OpenAI(api_key = "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")
        self.end_tokens = "!?.;"
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def message(self, message: str):

        self.messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(model="gpt-4o-mini", messages = self.messages, stream=True, temperature=0.7, top_p=0.8)
        answer = ""
        sentence = ""

        for chunk in response:

            if content:=chunk.choices[0].delta.content:

                print(sentence)

                sentence+=content

                if any(token in content for token in self.end_tokens):

                    print("sending!!!", sentence)

                    yield sentence

                    answer+=sentence
                    sentence = ""

        print("getting out")
        
        if sentence: yield sentence

        self.messages.append({"role": "assistant", "content": answer})

def float2pcm(sig, dtype='int16'):
    sig = sig.detach().cpu().numpy()
    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)

class RealtimeVoice(AudioSource):

    def __init__(self, text):
        self.stream = io.BytesIO()
        self.lock = threading.Lock()
        self.inference_loop = threading.Thread(target=self.inference, args=(text, ))
        self.inference_loop.start()

    def inference(self, text):
        for sentence in text:
            chunks = voice_model.inference_stream(sentence, "ru", gpt_cond_latent, speaker_embedding, temperature=0.2, top_p=0.1)
            for chunk in chunks:
                self.write(np.repeat(float2pcm(chunk), 4)) # convert mono 24khz to stereo 48khz

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
            if len(ret) != OpusEncoder.FRAME_SIZE:
                return b""
            return ret
        
chat = Chat()

async def finished_callback(sink, user_id, audio, channel):
    print("received")

    t = time.time()

    transcribe, _ = model.transcribe(audio.file, language="ru")
    full_transcribe = ' '.join([segment.text for segment in transcribe])

    print(full_transcribe, time.time()-t)

    text = chat.message(full_transcribe)

    print(text, time.time()-t)

    audio = RealtimeVoice(text)

    await audio.wait_until_stream_is_not_empty()

    await sink.vc.play(audio)

    print("end")