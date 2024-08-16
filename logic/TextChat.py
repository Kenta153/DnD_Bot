from openai import OpenAI
from config import OPENAI_TOKEN, INITIAL_PROMPT

class Chat:

    client = OpenAI(api_key = OPENAI_TOKEN)
    end_tokens = "!?.;"
    messages = []
    if INITIAL_PROMPT:
        messages.append({"role": "system", "content": INITIAL_PROMPT})

    @classmethod
    def message(cls, message: str):
        cls.messages.append({"role": "user", "content": message})

    @classmethod
    def process(cls):

        yield "Анекдот!"
        yield "Еврея приговорили к смертной казни"

        # response = cls.client.chat.completions.create(model="gpt-4o-mini", messages = cls.messages, stream=True, temperature=0.8, top_p=0.8)
        # answer = ""
        # sentence = ""

        # for chunk in response:

        #     if content:=chunk.choices[0].delta.content:

        #         for token in cls.end_tokens:

        #             if token in content:

        #                 parts = content.split(token)

        #                 yield sentence+parts[0]+token.replace(".", "..")

        #                 sentence = parts[1]

        #                 break
                
        #         else:
        #             sentence += content
        #             answer += content
        
        # if sentence and sentence != " ": yield sentence

        # cls.messages.append({"role": "assistant", "content": answer})