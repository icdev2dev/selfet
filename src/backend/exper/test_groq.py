import os
import json
            

from typing import Annotated, List


from tools_utils import tools_function, include_all_tools_functions, groq_chat


MODEL_N1 = "llama3-groq-70b-8192-tool-use-preview"

#MODEL_N1 = "llama3-groq-8b-8192-tool-use-preview"
MODEL_N2 = "llama3-70b-8192"

TOOLS_FUNCTIONS = {}

def get_enums_from_description(vars: List):
    """
    This function extracts the enums of a specific variables as described in the description. These enums 
    are usually described in the following examples.

    # Example 1
    ## The city must be one of ["London", "Boston", "NewYork]. 
    ### The variable is city
    ### The enum is  ["London", "Boston", "NewYork]

    # Example 2
    ## The country must be one of ["UK", "USA"].
    ### The variable is country
    ### The enum is ["UK", "USA"]

    # Example 3
    ## The zipcode is one in the following set of zipcodes ["94001", "94002"]
    ### The variable is zipcode 
    ### The enum is ["94001", "94002"]

    
    Obviously the above are just examples. The variables and their enums will be named differently in the
    actual description. When you extract different variables, you must use string representation such as 
    '{variable: 'zipcode', enum: ["94001", "94002"] }' populated in the vars


    """


@tools_function(TOOLS_FUNCTIONS)
def call_agents(
        target_agent: Annotated[str, "This is the target agent; the subject in the text"],
        source_agent: Annotated[str, "This is the source agent; the object in the text"] = ""
):
    """ This function MAY have multiple target_agents and if it has a target agent, it MAY have source_agents. 
    ALL agents are explicity mentioned in the text; ALWAYS prefixed by '@'. The distinction between the 
    two types of agents is VERY important. The target agent can be thought about as the subject in advait 
    vedanta and the source agent is the object in adavit vedanta. The text is always requesting the target 
    agent to do something. The source agent may make further references to other agents. Please ignore other
    such agents. Please prefix all agents by '@' before returning. It's ok if you don't have a source agent. 
    Please don't create source agents for the sake of it.  ALL source agents, if present, are explicitly 
    mentioned. Some times both target agents are mentioned in the same sentence. 
    
    The target_agents can ALSO be seperated by a single or multiple sentences.
    For example in : 
        ## @tina: Can you please look at the site plan, This is @ethan. Oh, @john, can you please provide input on the site plan
        ### target_agents are @tina and @john


        For example: 
            # In 
            ## Hi @agent1 can you post something on forum 
            ### the target_agent is @agent1
            
            ## Hi @agent2. I am @agent3. Can you please review my essay? 
            ### The target_agent is @agent2
            ### The source_agent is @agent3

            ## The situation is that there is a fire on the street. The fire fighters are getting ready.
            ### There are NO target_agents and NO source agents

            ## The sky is an ominous mix of dark smoke and ash, partially obscuring the sun and casting an eerie, orange glow over the landscape. The air is thick with the smell of burning wood, and the crackling of flames can be heard even from a distance. Trees are ablaze, and embers are carried by the wind, creating spot fires that add to the chaos.
            ### There are NO target_agents and NO source agents

            
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
        subject in the second person. Take the totality of the entire context. The pure objective could be multi fold. It is 
        much better to be explicit for the entire context.
        This function MAY have multiple target_agents and if it has a target agent, it MAY have source_agents. TOTALLY REFRAIN FROM INCLUDING TARGET_AGENTS 
        AND SOURCE_AGENTS. ALL agents are explicity mentioned in the text; typically prefixed by '@'. The distinction between the two types of agents is VERY important. The target agent 
        can be thought about as the subject in advait vedanta and the source agent is the object in adavit vedanta. The text is always 
        requesting the target agent to do something. The source agent may make further references to other agents. 
        PLEASE DISCOUNT ANY SUCH AGENTS (either TARGET_AGENT or SOURCE_AGENT) while forming the description.
        
    """
    data = {'description': description}
    return json.dumps(data)


tools = include_all_tools_functions(TOOLS_FUNCTIONS)



def identify_target_agents(user_prompt):
    chat_model = groq_chat
    
    
    messages=[
            {
             "role": "user",
                "content": user_prompt,
            }
        ]
    
    chat_completion = chat_model.chat.completions.create(
        messages = messages,
        model=MODEL_N1,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "call_objective"}}
    )


def find_agents(chat_model, user_prompt):
    messages=[]
    messages.append({'role': 'user', 'content': user_prompt})

    chat_completion = chat_model.chat.completions.create(
        messages = messages,
        model=MODEL_N1,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "call_agents"}}
    )

    target_agents = set()
    source_agents = set()

    if chat_completion.choices[0].message.tool_calls:

        tool_calls = chat_completion.choices[0].message.tool_calls

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments
            function_args = json.loads(function_args)

            function = TOOLS_FUNCTIONS[function_name]['function']

            function_response = function(**function_args)

            function_response = json.loads(function_response)


            import re
            proposed_target_agent = function_response['target_agent']

            if re.match(r".*,.*", proposed_target_agent) : 
                for target_agent in [x.strip() for x in re.split(",", proposed_target_agent)] : 
                    target_agents.add(target_agent)
            else :
                target_agents.add(proposed_target_agent)

            if function_response['source_agent'] != "":
                source_agents.add(function_response['source_agent'])

#    print(target_agents)
#    print(source_agents)

    return target_agents, source_agents






def find_call_objective(chat_model, user_prompt):
    messages=[]
    messages.append({'role': 'user', 'content': user_prompt})

    chat_completion = chat_model.chat.completions.create(
        messages = messages,
        model=MODEL_N1,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "call_objective"}}
    )

    first_response = ""

    if chat_completion.choices[0].message.tool_calls:

        tool_calls = chat_completion.choices[0].message.tool_calls
        tool_call = tool_calls[0]

        function_name = tool_call.function.name
        function_args = tool_call.function.arguments
        function_args = json.loads(function_args)

        function = TOOLS_FUNCTIONS[function_name]['function']

        function_response = function(**function_args)

        first_response = function_response
#    print(json.loads(first_response)['description'])

    return first_response

    

def process_system_prompt_1(chat_model, user_prompt):

    call_objective = find_call_objective(chat_model=chat_model, user_prompt=user_prompt)
    print(call_objective)
    target_agents, source_agents = find_agents(chat_model=chat_model, user_prompt=user_prompt)

    print(target_agents)


def process_system_prompt(chat_model, user_prompt):

    messages=[]
    messages.append({'role': 'user', 'content': user_prompt})

    chat_completion = chat_model.chat.completions.create(
        messages = messages,
        model=MODEL_N1,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "call_agents"}}
    )

    if chat_completion.choices[0].message.tool_calls:

        tool_calls = chat_completion.choices[0].message.tool_calls

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments
            function_args = json.loads(function_args)

            function = TOOLS_FUNCTIONS[function_name]['function']

            function_response = function(**function_args)


            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )


            second_response = chat_model.chat.completions.create(
                model=MODEL_N2, messages=messages
            )

            print("\n\nSecond LLM Call Response:", second_response.choices[0].message.content)
            

if __name__ == "__main__":
    while True:
        user_prompt = input("> ")
        process_system_prompt_1(groq_chat, user_prompt=user_prompt)


 




