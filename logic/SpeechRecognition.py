import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

from faster_whisper import WhisperModel
from config import WHISPER_MODEL

class Recognition:

    model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")

    @classmethod
    def transcribe(cls, audio):
        transcribe, _ = cls.model.transcribe(audio, language="ru", vad_filter=True)
        full_transcribe = ' '.join([segment.text for segment in transcribe])

        return full_transcribe