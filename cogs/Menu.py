from discord.ext import commands
import discord
from logic.SpeechGeneration import Speech
import io

class Menu(commands.Cog):

    def __init__(self):
        self.voice_file_uploading = False

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        # Найти основной текстовый канал сервера
        if guild.system_channel is not None:
            channel = guild.system_channel
        else:
            # Если основной канал не установлен, выбираем первый доступный канал
            channel = next((channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages), None)

        if channel is not None:
            await channel.send(
                f"Привет, **{member.name}**! Я - **Dnd Game Bot**, искусственный интеллект, предназначенный для игры в Подземелья и Драконы! \nВот список доступных команд: \n\
                **/create_thread** - *Создаёт отдельную ветку с ботом и пользователем*\n\
                **/join**          - *Подключает бота к голосовому каналу*\n\n\
                Также, если Вы хотите **поменять** голос рассказчика, то Вы можете **прислать** аудиофайл с желаемым голосом, размером в 10-20 секунд."
            )
            
    # @commands.slash_command()
    # async def create_thread(self, ctx):
    #     user = ctx.author
    #     thread = await ctx.channel.create_thread(name=f"Профиль", type=discord.ChannelType.private_thread, invitable=False)
    #     await thread.add_user(user)
    #     await thread.send(f"Привет, {user.name}! Это ваша личная переписка.")


    @commands.slash_command()
    async def custom_voice(self, ctx):
        self.voice_file_uploading = True
        await ctx.respond("Загрузи аудио-файл с желаемым голосом диктора. Рекомендуемая продолжительность - 10-15 секунд.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.voice_file_uploading and not message.author.bot:
            print(message.attachments, message.attachments[0].content_type)
            if len(message.attachments)==1 and "audio" in message.attachments[0].content_type:

                voice = io.BytesIO()

                await message.attachments[0].save(voice, use_cached=True)

                Speech.new_voice([voice])
                self.voice_file_uploading = False
                
                await message.channel.send("Голос сохранен успешно!")
            else:
                await message.channel.send("Произошла ошибка. Попробуй еще раз. Прикрепи один аудио-файл с желаемым голосом диктора.")

def setup(bot):
    print("Menu loaded!")
    bot.add_cog(Menu())