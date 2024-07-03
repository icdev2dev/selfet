import os
import json
            

from groq import Groq
from openai import OpenAI
from typing import Annotated


from tools_utils import tools_function, include_all_tools_functions

TOOLS_FUNCTIONS = {}

@tools_function(TOOLS_FUNCTIONS)
def call_agent(
        target_agent: Annotated[str, "This is the target agent; the subject in the text"],
        source_agent: Annotated[str, "This is the source agent; the object in the text"] = ""
):
    """ This function calls an agent with an input thread and, optionally, an output thread. The agent is explicity 
        mentioned in the text; typically prefixed by '@'. We can call this the target agent. There can also be a source
        agent; also prefixed by '@'. The distinction between the two types of agents is VERY important. The target agent 
        can be thought about as the subject in advait vedanta and the source agent is the object in adavit vedanta. The text is always 
        requesting the target agent to do something. The source agent may make further references to other agents. Please ignore other
        such agents.

        For example: 
            In Hi @agent1 can you post something on forum, the target agent is @agent1
            In Hi @agent2. I am @agent3. Can you please review my essay?, the target agent is @agent2 and 
                source agent is @agent3

    """

    data = {'target_agent': target_agent,
            'source_agent': source_agent
            }
    return json.dumps(data)


@tools_function(TOOLS_FUNCTIONS)
def call_objective(
    description: Annotated[str, "the description describes the PURE objective in the prompt. The description should be couched as a request to the subject in the second person. "]
    ):
    """ This function describes the PURE objective in the prompt. The description should be couched as a request to the 
        subject in the second person. 
        
    """
    data = {'description': description}
    return json.dumps(data)

@tools_function(TOOLS_FUNCTIONS)
def get_cost_of_running_a_thread_on_a_model(
        provider: Annotated[str, "This is the provider providing the model such as openai/groq. default is openai"],
        model: Annotated[str, "This is the model in description. This is typically prefixed by %"],
        thread: Annotated[str, "This is the thread whose cost is required. This is typically prefixed with !"]        
        ):
    """ This function provides the cost of running a thread on a model. Because the cost varies by different providers
        with different SLAS, it is important to identify the provider from the prompt. The default provider is openai; 
        but could be different such as groq, google, etc. 
        
        If the provider is openai, the default model is gpt-4-turbo. If the provider is groq, the default model is llama3-8b-8192.
        else If the provider is google, the default model is gemini-it.         
    """
    return f"{provider} {model} {thread}"




tools = include_all_tools_functions(TOOLS_FUNCTIONS)



tools_minus = []

for tool in tools:

    tool_function = tool['function']
    tool_function.pop('function')

    tools_minus.append(tool)




client_openai = OpenAI()
client_groq = Groq()

class ChatAPIWrapper:
    def __init__(self, client):
        self.chat = self.Chat(client.chat)

    class Chat:
        def __init__(self, chat):
            self.completions = chat.completions


groq_chat = ChatAPIWrapper(client=client_groq)
openai_chat = ChatAPIWrapper(client=client_openai)



def process_system_prompt(chat_model, user_prompt):

    messages=[
            {
                "role": "system",
                "content": "You am a math tutor. Your name is Mani. You can ask for feedback from alina, freda or john by prefixing their names with '@'. You can choose none or more members for feedback on a pro active basis. Please think step by step to articulate specific feedback requested from team members. i.e. why you need feedback and what would successful feedback look like. "
            },

            {
             "role": "user",
                "content": user_prompt,
            }
        ]
    chat_completion = chat_model.chat.completions.create(
        messages = messages,
        model="llama3-8b-8192",
        tools=tools_minus,
        tool_choice={"type": "function", "function": {"name": "call_objective"}}
    )

    if chat_completion.choices[0].message.tool_calls:

        tool_calls = chat_completion.choices[0].message.tool_calls

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments
            function_args = json.loads(function_args)

            function = TOOLS_FUNCTIONS[function_name]['function']


            function_response = function(**function_args)

            print(function_response)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )


            second_response = chat_model.chat.completions.create(
                model="llama3-8b-8192", messages=messages
            )

            print("\n\nSecond LLM Call Response:", second_response.choices[0].message.content)
if __name__ == "__main__":
    while True:
        user_prompt = input("> ")
        process_system_prompt(groq_chat, user_prompt=user_prompt)


 




