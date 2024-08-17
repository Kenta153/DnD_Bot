from discord.ext import commands
from utils import custom_wave_sink
from logic.SpeechGeneration import Speech
from logic.SpeechRecognition import Recognition
from logic.TextChat import Chat

class Voice(commands.Cog):

    @commands.slash_command(name="join", description="Подключает бота к голосовому каналу")
    async def join(self, ctx):
        voice = ctx.author.voice

        if not voice:
            return await ctx.respond("*Ты не находишься в голосовом канале!*")

        vc = await voice.channel.connect()

        vc.start_recording(
            custom_wave_sink.WaveSink(),
            self.finished_callback,
            ctx.channel,
        )

        await ctx.respond("*Наше приключение начинается...*")

    async def finished_callback(self, sink, user_id, audio, channel):

        transcribation = Recognition.transcribe(audio.file)

        if not transcribation:
            return

        Chat.message(transcribation)

        if not sink.audio_data:
        
            audio = await Speech.process(Chat.process())

            await sink.vc.play(audio)

def setup(bot):
    print("Voice loaded!")
    bot.add_cog(Voice())