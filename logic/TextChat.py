import openai
from config import OPENAI_TOKEN, INITIAL_PROMPT
import json
from logic import MusicBot
import asyncio
import base64
import io
import discord
import threading

FUNCTIONS = {
    "set_music": {
        "name": "set_music",
        "description": "Устанавливает музыку",
        "parameters": {
            "type": "object",
            "properties": {
                "music_type": {
                    "type": "string",
                    "description": "Один из типов музыки: exploring, travelling, normal_combat, epic_compat, boss_battle, town, temple, tavern, boat_shanties, desert, forest, ice_and_snow, swamp_marshes, creepy_horror, None.",
                },
            },
            "required": ["music_type"],
        },
    },
    "create_image": {
        "name": "create_image",
        "description": "Создаёт картинку",
        "parameters": {
            "type": "object",
            "properties": {
                "image_prompt": {
                    "type": "string",
                    "description": "Описание картинки",
                },
            },
            "required": ["image_prompt"],
        },
    },
    "end_game": {
        "name": "end_game",
        "description": "Заканчивает приключение",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

FUNCTIONS_FOR_API = list(FUNCTIONS.values())

def set_music(music_type: str):
    if music_type == "None":
        MusicBot.kill()
        return str("Музыка выключена!")
    elif music_type in MusicBot.sources:
        if music_type != MusicBot.music_key:
            MusicBot.play(music_type)
        print("Включаем музыку!")
        return str(f"Играет музыка: {music_type}!")
    else:
        print("Неверный тип музыки!")
        return str("Неверный тип музыки!")
    
async def create_image(image_prompt: str):

    response = await openai.Image.acreate(
            model="dall-e-3",
            prompt=image_prompt,
            response_format="b64_json",
            quality="standard",
            size='1024x1024',
            n = 1
    )
    print("created")
    image_b64 = response["data"][0]["b64_json"]
    image_bytes = io.BytesIO(base64.b64decode(image_b64))
    picture = discord.File(fp=image_bytes, filename="image.png")

    await Chat.channel.send(file=picture)

async def end_game():
    Chat.killed = True

    return str("Расскажи послесловие!")
    

def call_function(loop, function_name: str, function_arguments: str) -> str:
    """Calls a function and returns the result."""

    # Ensure the function is defined
    if function_name not in FUNCTIONS:
        return "Function not defined."

    # Convert the function arguments from a string to a dict
    function_arguments_dict = json.loads(function_arguments)

    # Ensure the function arguments are valid
    function_parameters = FUNCTIONS[function_name]["parameters"]["properties"]
    for argument in function_arguments_dict:
        if argument not in function_parameters:
            return f"{argument} not defined."
        
    if function_name == "create_image":
        loop.create_task(globals()[function_name](**function_arguments_dict))
        return "Image created!"
    elif function_name == "set_music":
        return globals()[function_name](**function_arguments_dict)

    # Call the function and return the result
    return asyncio.run_coroutine_threadsafe(globals()[function_name](**function_arguments_dict), loop).result()

class Chat:

    openai.api_key = OPENAI_TOKEN
    end_tokens = "!?.;"
    messages = [{"role": "system", "content": INITIAL_PROMPT}]
    killed = False
    bot = None
    running = True

    @classmethod
    def message(cls, message: str):
        cls.messages.append({"role": "user", "content": message})

    @classmethod
    def process(cls, loop, channel, vc):
        cls.running = True
        cls.channel = channel

        response = openai.ChatCompletion.create(model="gpt-4o-mini", messages = cls.messages, stream=True, temperature=0.8, top_p=0.8, functions=list(FUNCTIONS.values()))
        answer = ""
        sentence = ""

        function_call = {"name": "", "arguments": ""}

        for chunk in response:

            msg = chunk["choices"][0]

            if "delta" in msg:

                if "function_call" in msg["delta"]:
                    if "name" in msg["delta"]["function_call"]:
                        function_call["name"] += msg["delta"]["function_call"]["name"]
                    if "arguments" in msg["delta"]["function_call"]:
                        function_call["arguments"] += msg["delta"]["function_call"]["arguments"]
                    

                elif "content" in msg["delta"]:

                    content = msg["delta"]["content"]

                    for token in cls.end_tokens:

                        if token in content:

                            parts = content.split(token)

                            yield (sentence+parts[0]+token.replace(".", "..    ")).lstrip()

                            sentence = parts[1]

                            break
                    
                    else:
                        sentence += content
                        answer += content

            if msg["finish_reason"] == "stop":
                if sentence and sentence != " ": yield sentence.strip()
                if not cls.killed:
                    cls.messages.append({"role": "assistant", "content": answer})
                else:
                    asyncio.run_coroutine_threadsafe(channel.send("**Вы закончили ваше приключение...**\nНадеемся, что оно было увлекательным! :fire:\n*Если Вы хотите начать новую игру, то вновь пригласите бота в голосовой канал*"))
                    asyncio.run_coroutine_threadsafe(vc.disconnect(), loop)
                    cls.messages = cls.messages[0]
                    cls.killed = False

            elif msg["finish_reason"] == "function_call":
                print("calling function")
                function_output = call_function(
                    loop, function_call["name"], function_call["arguments"]
                )
                cls.messages.append(
                    {
                        "role": "function",
                        "content": function_output,
                        "name": function_call["name"],
                    }
                )
                yield from cls.process(loop, channel, vc)

        cls.running = False