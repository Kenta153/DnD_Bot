from discord.ext import commands
import discord
from logic import custom_wave_sink
from logic.callback import finished_callback
from music_bot import play

class Menu(commands.Cog):

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Найти основной текстовый канал сервера
        if guild.system_channel is not None:
            channel = guild.system_channel
        else:
            # Если основной канал не установлен, выбираем первый доступный канал
            channel = next((channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages), None)

        if channel is not None:
            await channel.send(f"""Привет, {guild.name}! Спасибо за добавление меня на ваш сервер! \n
                               Вот список доступных команд: \n""")
            
    @commands.slash_command()
    async def create_thread(self, ctx):
        user = ctx.author
        thread = await ctx.channel.create_thread(name=f"Профиль", type=discord.ChannelType.private_thread, invitable=False)
        await thread.add_user(user)
        await thread.send(f"Привет, {user.name}! Это ваша личная переписка.")

    @commands.slash_command()
    async def join(self, ctx):
        voice = ctx.author.voice

        if not voice:
            return await ctx.respond("You're not in a vc right now")
        
        await play(voice.channel.id, "exploring")

        print("lll")

        vc = await voice.channel.connect()

        print("lll")

        vc.start_recording(
            custom_wave_sink.WaveSink(),
            finished_callback,
            ctx.channel,
        )

        print("lll")

        await ctx.respond("The recording has started!")

def setup(bot):
    bot.add_cog(Menu())