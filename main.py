from utils import discord_patch
discord_patch.patch()

import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN
from logic.MusicBot import bot2
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(intents=intents) 

@bot.event
async def on_ready():
    print(f'Logged as {bot.user}')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    bot.load_extension("cogs")
    loop.create_task(bot.start(DISCORD_BOT_TOKEN)) 
    loop.create_task(bot2.start("MTI3MTEwMzg2MDM2MjA1NTcxMQ.GD6h0c.vEkC905JFdaXhfkV2gGigipbygSC6Y_m6C8E3I"))
    loop.run_forever()