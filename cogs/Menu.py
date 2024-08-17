from discord.ext import commands
import discord
from logic.SpeechGeneration import Speech
from logic.TextChat import Chat
import io

class Menu(commands.Cog):

    def __init__(self):
        self.voice_file_uploading = False
        self.story_text_uploading = False

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        
        # Найти основной текстовый канал сервера
        if guild.system_channel is not None:
            channel = guild.system_channel
        else:
            # Если основной канал не установлен, выбираем первый доступный канал
            channel = next((channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages), None)

        if channel is not None:
            await channel.send(
                f"Привет, **{member._user.global_name}**! Я - **Dnd Game Bot**, искусственный интеллект, предназначенный для игры в Подземелья и Драконы!\nВот список доступных команд:\n**/create_thread** - *Создаёт отдельную ветку с ботом и пользователем*\n**/start** - *Подключает бота к голосовому каналу*\n**/stop** - *Останавливает игру*\n\nТакже, если Вы хотите **поменять** голос рассказчика, то Вы можете **прислать** аудиофайл с желаемым голосом, размером в 10-20 секунд."
            )

    @commands.slash_command(name = "custom_voice", description="Загрузи голос диктора!")
    async def custom_voice(self, ctx):
        self.voice_file_uploading = True
        await ctx.respond(
        "*Пожалуйста :pray:, пришли аудио-файл с желаемым голосом рассказчика.*\n**Рекомендуемая** продолжительность аудио-файла: **15-20** сек."
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return
        
        if self.voice_file_uploading:

            if len(message.attachments)==1 and "audio" in message.attachments[0].content_type:

                voice = io.BytesIO()

                await message.attachments[0].save(voice, use_cached=True)

                Speech.new_voice([voice])
                self.voice_file_uploading = False
                
                await message.channel.send("***Голос успешно сохранен! :muscle:***")
            else:
                await message.channel.send("**Внимание**:warning:\n***Произошла ошибка***:exclamation:\n*Проверьте, пожалуйста, прикрепили ли Вы один аудио-файл?*")
        elif self.story_text_uploading:

            Chat.messages.append({"role": "system", "content": "Вот предыстория, которую ты должен произнести!"})

            self.story_text_uploading = False

            await message.channel.send("*Новая История успешно сохранена!*")

    @commands.slash_command(name="custom_story", description="Загрузить свою историю!")
    async def custom_story(self, ctx):
        self.story_text_uploading = True
        await ctx.respond("***Пришлите новое развитие вашей истории в текстовом формате.***\n*Распишите как можно больше событий и увлекательных приключений!* :dizzy:")

def setup(bot):
    bot.add_cog(Menu())
    print("Menu loaded!")