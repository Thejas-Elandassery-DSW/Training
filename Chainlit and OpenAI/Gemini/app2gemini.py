import os
import google.generativeai as genai
import chainlit as cl

# Configure Gemini API
genai.configure(api_key="apikeyhere")

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')

@cl.on_message
async def on_message(message):
    # Generate response from Gemini
    response = model.generate_content(message.content)
    
    # Send response back to the user
    await cl.Message(content=response.text).send()

if __name__ == "__main__":
    cl.run()