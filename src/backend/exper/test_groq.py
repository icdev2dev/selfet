import os
import json
            

from typing import Annotated, List


from tools_utils import tools_function, include_all_tools_functions, groq_chat


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






def execute_function_calling(chat_model, model, function_name, messages):

    pass

def identify_target_agents(user_prompt):
    chat_model = groq_chat
    model = "llama3-8b-8192"
    function_name = ""
    messages=[
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



def process_system_prompt(chat_model, user_prompt):

    messages=[
            {
                "role": "system",
                "content": """

                You are a fire fighter. 
                Your name is Joe. Don't be theoritical. Execute immediate actions and relay instructions. 
                There is no "I". just do it. Always introduce yourself so that others know.

                You are a part of a team. The team consists of: 

                Alan (Team Leader): Equipped with a communication device, map, and firefighting gear.
                Mani: Expert in handling hoses and water supply.
                Sarah: Specialist in creating firebreaks and using controlled burns.
                John: Medic, trained in first aid and emergency response.
                Joe : Logistics, responsible for coordinating supplies and equipment.

                # listen for emergencies
                # dispatch to emergency if required
                # engage in emergency
                # resolve emergency
                """

            },

            { 
                "role": "assistant", 
                "content":  """
The sky is an ominous mix of dark smoke and ash, partially obscuring the sun and casting an eerie, orange glow over the landscape. The air is thick with the smell of burning wood, and the crackling of flames can be heard even from a distance. Trees are ablaze, and embers are carried by the wind, creating spot fires that add to the chaos.

                            """

            },


            {
                "role": "user",
                "content": """
 **ALERTE!**

Alright, let's get rolling!

**SITUATION REPORT**
Fire call "call_b6wk" - Identify origin and provide aid


Mani, can you detach the hoses from the fire engine and prepare for a search-and-rescue operation?

Sarah, get ready to create a firebreak and contain the blaze's spread. Assemble a fire extinguishing team.

John, report to the affected area to assess injuries and provide medical aid as needed.

Joe, coordinate the delivery of emergency supplies, including water, food, and medical kits.

                """
            },
            {
                "role": "assistant", 
                "content": """
I'm Mani, firefighter. I've detached the hoses from the fire engine and I'm ready to prepare for a search-and-rescue operation. I've got my gear ready, and I'm investigating the origin of the fire to get a better understanding of the situation.
"""
            },
            {
                "role": "assistant",
                "content": """
It seems our priority is to identify the origin of the fire.

**SARAH HERE**

I'll move in to assess the area and find the source of the fire. I'll report back with my findings.
"""
            },
            {
                "role": "assistant", 
                "content": """
**SARAH HERE**

I've made my way to the source of the fire and conducted a thorough investigation. I've found that the fire originated from a faulty electrical wire on the old wooden shed nearby. It's fortunate that the shed was largely intact, but the flames spread quickly due to the strong winds.

Recommendation: Alan, please relay this information to the team. We should aim to isolate the shed and focus our efforts on extinguishing the fire there first.

"""
            },

            {"role": "assistant",
             "content": """ 
 **ALAN, TEAM LEADER**

Alright, we've got our mission objective! Let's get to work.

To John:

Can you move in to assess the situation and provide medical aid to anyone injured in the area? We need to ensure everyone's safety.

To Sarah:

Create a firebreak around the shed to contain the blaze's spread. Use controlled burns if necessary.

To Mani:

Assemble a team to assist me in extinguishing the fire at the shed. We'll work together to put out the flames and prevent further spread.

To Joe:

Coordinate the delivery of emergency supplies, including water, food, and medical kits. Ensure our team has everything we need to complete this mission.

Let's move swiftly and efficiently. We can do this, team!
"""
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


 




