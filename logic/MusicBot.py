import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from pytube import Playlist
import random

music_bot = commands.Bot()

ffmpeg_options = {'options': '-vn'}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': True,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
sources = {
    "exploring": "https://www.youtube.com/playlist?list=PLga5e6HS7U3aiSCeRb8nkQ-ZOKM3gwU4X",
    "travelling": "https://www.youtube.com/playlist?list=PLga5e6HS7U3bjASdROry46emz0MTRD9TB",
    "normal_combat": "https://www.youtube.com/playlist?list=PLga5e6HS7U3bqTSSav_tshPj89Jxu4_Ld",
    "epic_compat": "https://www.youtube.com/playlist?list=PLga5e6HS7U3aO0m_xqIXhAJ9qUeIpkLZH",
    "boss_battle": "https://www.youtube.com/playlist?list=PLga5e6HS7U3YGM2nBm8SeZKnJmCXUzFgf",
    "town": "https://www.youtube.com/playlist?list=PLga5e6HS7U3Zja5HQDpUg5gqe2chgQg4m",
    "temple": "https://www.youtube.com/playlist?list=PLga5e6HS7U3bcyK1N3TrJO8LGNVmI42F6",
    "tavern": "https://www.youtube.com/playlist?list=PLga5e6HS7U3YFuQd97SJf-OfMF-nOdICj",
    "boat_shanties": "https://www.youtube.com/playlist?list=PLga5e6HS7U3ZJUqtDbanTqZLBTbEnAbjE",
    "desert": "https://www.youtube.com/playlist?list=PLga5e6HS7U3Yh8GO3SSkdHI7KhtIkA21f",
    "forest": "https://www.youtube.com/playlist?list=PLga5e6HS7U3Zg8MdDVyzzcdFgD7ZOFJHe",
    "ice_and_snow": "https://www.youtube.com/playlist?list=PLga5e6HS7U3ZQIuUN-rhMjZMZUBT9KPNE",
    "swamp_marshes": "https://www.youtube.com/playlist?list=PLga5e6HS7U3aosjXCvQc6KYoFgfYoGu1Y",
    "creepy_horror": "https://www.youtube.com/playlist?list=PLga5e6HS7U3YX3yHWXhl3WAe0mmIFavMe",
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
music_key = None

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source: discord.AudioSource, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    def from_url(cls, url, *, stream=False):
        playlist = Playlist(url)
        song_info = ytdl.extract_info(random.choice(playlist), download=not stream)

        return cls(discord.FFmpegPCMAudio(song_info["url"], **ffmpeg_options, executable="ffmpeg\\ffmpeg.exe"), data=song_info)
    
async def join(channel_id):
    if not music_bot.voice_clients:
        try:
            voice_channel = music_bot.get_channel(channel_id)
            await voice_channel.connect()
        except:
            print('Уже подключен или не удалось подключиться')


def play(key):

    url = sources[key]

    voice_client: discord.VoiceClient = music_bot.voice_clients[0]

    if voice_client._player:
        voice_client._player.after = None
        voice_client.stop()

    source = YTDLSource.from_url(url, stream=True) 
    voice_client.play(source, after=lambda e: play(key))

def kill():
    voice_client: discord.VoiceClient = music_bot.voice_clients[0]
    if voice_client._player:
        voice_client._player.after = None
        voice_client.stop()
