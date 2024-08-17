import discord
from discord.sinks.core import RawData
import time
import select
import struct
from discord import opus
import asyncio
from logic.SpeechGeneration import Speech

def recv_audio(self, sink, callback, *args):
    # Gets data from _recv_audio and sorts
    # it by user, handles pcm files and
    # silence that should be added.

    self.user_timestamps: dict[int, tuple[int, float]] = {} # type: ignore
    self.starting_time = time.perf_counter()
    self.first_packet_timestamp: float # type: ignore
    while self.recording:
        ready, _, err = select.select([self.socket], [], [self.socket], 0.01)
        if not ready:
            if err:
                print(f"Socket error: {err}")
            continue

        try:
            data = self.socket.recv(4096)
        except OSError:
            self.stop_recording()
            continue

        self.unpack_audio(data, sink, callback, *args)

def recv_decoded_audio(self, data: RawData):
    # Add silence when they were not being recorded.
    if data.ssrc not in self.user_timestamps:  # First packet from user
        asyncio.run_coroutine_threadsafe(Speech.kill(), self.loop)
        if (
            not self.user_timestamps or not self.sync_start
        ):  # First packet from anyone
            self.first_packet_timestamp = data.receive_time
            silence = 0

    else:  # Previously received a packet from user
        dRT = (
            data.receive_time - self.user_timestamps[data.ssrc][1]
        ) * 48000  # delta receive time
        dT = data.timestamp - self.user_timestamps[data.ssrc][0]  # delta timestamp
        diff = abs(100 - dT * 100 / dRT)
        if (
            diff > 60 and dT != 960
        ):  # If the difference in change is more than 60% threshold
            silence = dRT - 960
        else:
            silence = dT - 960

    self.user_timestamps.update({data.ssrc: (data.timestamp, data.receive_time)})

    data.decoded_data = (
        struct.pack("<h", 0) * max(0, int(silence)) * opus._OpusStruct.CHANNELS
        + data.decoded_data
    )

    while data.ssrc not in self.ws.ssrc_map:
        time.sleep(0.05)
    self.sink.write(data.decoded_data, self.ws.ssrc_map[data.ssrc]["user_id"])

def unpack_audio(self, data, sink, callback, *args):
    """Takes an audio packet received from Discord and decodes it into pcm audio data.
    If there are no users talking in the channel, `None` will be returned.

    You must be connected to receive audio.

    .. versionadded:: 2.0

    Parameters
    ----------
    data: :class:`bytes`
        Bytes received by Discord via the UDP connection used for sending and receiving voice data.
    """
    if 200 <= data[1] <= 204:
        # RTCP received.
        # RTCP provides information about the connection
        # as opposed to actual audio data, so it's not
        # important at the moment.
        return
    
    if self.paused:
        return

    data = RawData(data, self)

    while data.ssrc not in self.ws.ssrc_map:
        time.sleep(0.05)

    if args[1].get_user(self.ws.ssrc_map[data.ssrc]["user_id"]).bot:
        return

    if data.decrypted_data == b"\xf8\xff\xfe":  # Frame of silence

        if data.ssrc not in self.user_timestamps:
            return
        
        self.user_timestamps.pop(data.ssrc)
        
        user_id = self.ws.ssrc_map[data.ssrc]["user_id"]

        if user_id not in sink.audio_data:
            return

        audio = sink.audio_data.pop(user_id)
        audio.cleanup()
        sink.format_audio(audio)

        callback = asyncio.run_coroutine_threadsafe(callback(sink, user_id, audio, *args), self.loop)

        return
    

    self.decoder.decode(data)


#monkey patching
def patch():
    discord.VoiceClient.unpack_audio = unpack_audio
    discord.VoiceClient.recv_audio = recv_audio
    discord.VoiceClient.recv_decoded_audio = recv_decoded_audio