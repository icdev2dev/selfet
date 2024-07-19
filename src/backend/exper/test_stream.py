import asyncio

from openai import OpenAI
from groq import Groq
from tools_utils import groq_chat

client = Groq()
#client = OpenAI()

DEPLOYMENT_MODEL ="llama3-8b-8192"

def get_available_functions():
    return {

    }


async def async_main():
    messages = [{"role": "system", "content": "User will provide a topic and you need to create a sales Pitch"},
                {"role": "user", "content": " Provide a sales pitch for google search engine "}
            ]
    
    stream =  client.chat.completions.create(messages=messages, model=DEPLOYMENT_MODEL, stream=True)

    # Convert the stream response to a list
    # stream_response1_list = [item async for item in stream]

    tool_calls = [] # Accumulator for tool calls to process later; 
    full_delta_content = "" # Accumulator for delta content to process later


    # Process the stream response for tool calls and delta content
    for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices and chunk.choices[0].delta is not None else None

        if delta and delta.content:
            full_delta_content += delta.content
            
        elif delta and delta.tool_calls:
            tc_chunk_list = delta.tool_calls
            for tc_chunk in tc_chunk_list:
                if len(tool_calls) <= tc_chunk.index:
                    tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                tc = tool_calls[tc_chunk.index]

                if tc_chunk.id:
                    tc["id"] += tc_chunk.id
                if tc_chunk.function.name:
                    tc["function"]["name"] += tc_chunk.function.name
                if tc_chunk.function.arguments:
                    tc["function"]["arguments"] += tc_chunk.function.arguments
    print(full_delta_content)

    # Step 2: check if the model wanted to call a function
    if not tool_calls and full_delta_content:
        messages.append({ "role": "assistant", "content": full_delta_content })

        # Convert the list to a stream to return as a response
        async def list_to_stream():
            for item in stream:
                print(item)
                yield item

        return list_to_stream()
    elif tool_calls:
        # Extend conversation by appending the tool calls to the messages
        messages.append({ "role": "assistant", "tool_calls": tool_calls })
        
        # Map of function names to the actual functions
        available_functions = get_available_functions() 

        for tool_call in tool_calls:

            # Note: the JSON response may not always be valid; be sure to handle errors
            function_name = tool_call['function']['name']
            if function_name not in available_functions:
                return "Function " + function_name + " does not exist"
    
        # Step 3: call the function with arguments if any
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call['function']['arguments'])
        function_response = function_to_call(**function_args)

        # Step 4: send the info for each function call and function response to the model
        messages.append(
            {
                "tool_call_id": tool_call['id'],
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

    stream_response2 = await client.chat.completions.create(
        model=DEPLOYMENT_MODEL,
        messages=messages,
        temperature=0,  # Adjust the variance by changing the temperature value (default is 0.8)
        top_p=0.95,
        max_tokens=4096,
        stream=True,
    )


    return stream_response2







def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
