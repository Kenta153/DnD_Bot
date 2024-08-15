import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

bot2 = commands.Bot()

ffmpeg_options = {'options': '-vn'}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': True,
    'quiet': True,
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
    "creepy_horror": "https://www.youtube.com/playlist?list=PLga5e6HS7U3YX3yHWXhl3WAe0mmIFavMe"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source: discord.AudioSource, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # Takes the first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

async def play(channel_id, key):
    url = sources[key]

    if not bot2.voice_clients:
        try:
            voice_channel = bot2.get_channel(channel_id)
            await voice_channel.connect()
        except:
            print('Уже подключен или не удалось подключиться')
            raise Exception("Hz error")

    voice_client = bot2.voice_clients[0]
    voice_client.stop()

    source = await YTDLSource.from_url("https://youtu.be/BOAuzWAd8Ok?si=_FuZXrigsEiKoIc6", loop = bot2.loop, stream=True) 
    print('source')
    voice_client.play(
        source, after=lambda e: print(f"Player error: {e}") if e else None
    )
    print("play")