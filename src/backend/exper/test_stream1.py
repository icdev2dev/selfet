import asyncio

from openai import OpenAI, AsyncOpenAI
from groq import Groq, AsyncGroq
from tools_utils import groq_chat

#client = Groq()
client = OpenAI()
client = AsyncOpenAI()
client = AsyncGroq()

DEPLOYMENT_MODEL ="llama3-70b-8192"

async def async_main():
    messages = [{"role": "system", "content": "User will provide a topic and you need to create a sales Pitch"},
                {"role": "user", "content": " Provide a sales pitch for google search engine "}
            ]
    
    stream = await client.chat.completions.create(messages=messages, model=DEPLOYMENT_MODEL, stream=True)

    full_delta_content = "" # Accumulator for delta content to process later

    # Process the stream response for tool calls and delta content
    async for  chunk  in stream:
        delta = chunk.choices[0].delta if chunk.choices and chunk.choices[0].delta is not None else None

        if delta and delta.content:
            full_delta_content += delta.content
            
    print(full_delta_content)

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
