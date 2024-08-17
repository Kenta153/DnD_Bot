import wave

from discord.sinks.core import Filters, Sink, default_filters


class WaveSink(Sink):
    """A special sink for .wav(wave) files.

    .. versionadded:: 2.0
    """

    def __init__(self, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        self.encoding = "wav"
        self.vc = None
        self.audio_data = {}

    def format_audio(self, audio):
        """Formats the recorded audio.

        Raises
        ------
        WaveSinkError
            Audio may only be formatted after recording is finished.
        WaveSinkError
            Formatting the audio failed.
        """
        data = audio.file

        with wave.open(data, "wb") as f:
            print(self.vc.decoder.CHANNELS, self.vc.decoder.SAMPLE_SIZE, self.vc.decoder.SAMPLING_RATE)
            f.setnchannels(self.vc.decoder.CHANNELS)
            f.setsampwidth(self.vc.decoder.SAMPLE_SIZE // self.vc.decoder.CHANNELS)
            f.setframerate(self.vc.decoder.SAMPLING_RATE)

        data.seek(0)
        audio.on_format(self.encoding)
