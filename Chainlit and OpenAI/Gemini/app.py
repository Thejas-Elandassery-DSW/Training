import os
from openai import OpenAI
import chainlit as cl

# Initialize the OpenAI client
client = OpenAI(
    api_key="")

@cl.on_message
async def on_message(message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.content}]
    )

    reply = response.choices[0].message.content

    await cl.Message(content=reply).send()

if __name__ == "__main__":
    cl.run()

    