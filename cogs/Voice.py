from discord.ext import commands
from utils import custom_wave_sink
from logic.SpeechGeneration import Speech
from logic.SpeechRecognition import Recognition
from logic.TextChat import Chat
from logic import MusicBot
import asyncio

import discord

discord.VoiceChannel

class Voice(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.killed = False
        self.vc = None

    @commands.slash_command(name="start", description="Подключает бота к голосовому каналу")
    async def join(self, ctx):
        voice = ctx.author.voice

        if not voice:
            return await ctx.respond("**Вы не находитесь в голосовом канале! :cry:**")
        
        
        await MusicBot.join(voice.channel.id)

        vc = await voice.channel.connect()

        self.vc = vc

        users = []
        for user_id in voice.channel.voice_states.keys():
            user = self.bot.get_user(user_id)
            if not user.bot:
                users.append(user.global_name)

        Chat.messages.append({"role": "system", "content": f"Вот список игроков: {','.join(users)}. Начинай игру!"})

        await ctx.respond(
        ":mage::woman_elf: **Ваше приключение начинается!** :park: :dragon_face::dragon_face:"
        )

        audio = await Speech.process(Chat.process(self.bot.loop, ctx.channel, vc))

        vc.play(audio)

        vc.start_recording(
            custom_wave_sink.WaveSink(),
            self.finished_callback,
            ctx.channel,
            self.bot
        )

    @commands.slash_command(name="stop", description="Плавно завершает игру!")
    async def stop(self, ctx):
        self.killed = True

        self.vc.stop_recording()
        while Chat.running:
            await asyncio.sleep(0.1)

        await ctx.respond("**Заканчиваю игру!** :dragon_face:")

        Chat.messages.append({"role": "system", "content": "Игроки, устали и больше не хотят играть. Придумай, как закончить игру на этом моменте, вызови функцию end_game и проговори концовку!."})
        audio = await Speech.process(Chat.process(self.bot.loop, ctx.channel))

        self.vc.play(audio)

        self.killed = False

        

    async def finished_callback(self, sink, user_id, audio, channel, bot):

        if self.killed:
            return

        transcribation = Recognition.transcribe(audio.file)

        print(transcribation)

        if not transcribation:
            return
        
        print("lalalala")

        Chat.message(f"{self.bot.get_user(user_id).global_name} сказал: {transcribation}")

        print("message!")

        if not sink.audio_data and "мастер" in transcribation.lower():

            print("audio!")
        
            audio = await Speech.process(Chat.process(self.bot.loop, channel, self.vc))

            await sink.vc.play(audio)

def setup(bot):
    bot.add_cog(Voice(bot))
    print("Voice loaded!")