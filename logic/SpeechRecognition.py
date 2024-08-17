import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

from faster_whisper import WhisperModel
from config import WHISPER_MODEL

BUGGED_SENTENCES = ["Субтитры сделал DimaTorzok", "Продолжение следует..."]

class Recognition:

    model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")

    @classmethod
    def transcribe(cls, audio):
        transcribe, _ = cls.model.transcribe(audio, vad_filter=True, language="ru")
        full_transcribe = ' '.join([segment.text for segment in transcribe if segment not in BUGGED_SENTENCES])

        return full_transcribe