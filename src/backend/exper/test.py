import json
from typing import Annotated, List
from tools_utils import tools_function, include_all_tools_functions, groq_chat, openai_chat, add_enum_to_param

TOOLS_FUNCTIONS = {}

@tools_function(TOOLS_FUNCTIONS)
def find_one_word_intent(
        intent: Annotated[str, "This is the one word intent in the prompt."]
):
    """
    The objective of this function is to find the one word intent in the given sentence/paragraph. This is done 
    essentially to distinguish between somemething new that is requested to be created or is a 
    request to update something. 

    The overall context is that the given sentence/paragraph is a direction to someone. There are only 
    two possible values, NEW and UPDATE: 

    # NEW: As mentioned earlier, this is a request to someone  to create something new
    ## i.e. can you provide your thoughts on how to improve our standards.
    ## i.e. Please give three novel ideas about the graphrag 
    ## etc...
    # UPDATE 
    ## i.e. what do you think about the recent post on the topic
    ## i.e. Can you provide some feedback on the above?
    ## etc...

    """
    data = {'one_word_intent': intent}
    return json.dumps(data)


@tools_function(TOOLS_FUNCTIONS)
def find_target_agents(
        target_agents: Annotated[str, "These are the target agents; the subjects in the text"]
):
    
    """ The agents is explicity mentioned in the text; typically prefixed by '@'. 
        In this function, we are focused on those target_agents that are subjects as in in advait vedanta 
        (aka target_agents). These target_agents are requested to do something. There can be multiple target_agents

        These target_agents are distinguished from source agent/s as in objects in advait vedanta. source agents are also present in the text. 
        But source agents should not reported. 

        Rules: 
        1. When someone introduces themselves, i.e. this is @mary,  @mary is NOT target_agents. 
        2. Sometimes the context is lookbefore. in @mary, this is @scott. Can you provide respond to @peter?, target_agent is @mary.

        Make special effort to distinguish target agents from source agents.
        Ensure that the white space is stripped from begining as well as a '@' is prefixed
            
            

    """

    data = {'target_agents': target_agents}

    return json.dumps(data)



@tools_function(TOOLS_FUNCTIONS)
def call_objective(
    description: Annotated[str, """The description describes the PURE objective. The description should be couched as a request to the subject/s in the second person. """]
    ):
    """ This function describes the PURE objective. The description should be couched as a 
    request to the subject/s in the second person.

    for example, 
        in case of "Hi @alina. Can you please provide feedback to my post", the decription is "provide feedback to a post"
 
    """
    data = {'call_objective': description}
    return json.dumps(data)



@tools_function(TOOLS_FUNCTIONS)
def get_enums_from_description(variable1: Annotated[str, "This is extracted JSON representation of the actual variable"], 
                               variable2: Annotated[str, "This is extracted JSON representation of the enums associated with the variable"]):
    """
    This function extracts the enums of a specific variable. These enums 
    are usually described in the following examples. The enums could be anywhere but within
    a single sentence. Just return JSON. 

    # Example 1
    ## The city must be one of ["London", "Boston", "NewYork]. 
    ### The variable1 is city
    ### The variable2 is  ["London", "Boston", "NewYork]

    # Example 2
    ## The country should be one of ["UK", "USA"].
    ### The variable1 is country
    ### The variable2 is ["UK", "USA"]


    # Example 4
    ## The request must be one of the following  ["NewRequest", "Feedback", "TakeAction"]
    ### The variable1 is request 
    ### The variable2 is ["NewRequest", "Feedback", "TakeAction"]
    
    Obviously the above are just examples. The variables and their enums will be named differently in the
    actual description. You may assume that only ONE var will be present. You MUST extract BOTH the vars and corresponding values.

    Also the MUST may be replaced with SHOULD.
    """

    print(variable1)
    print(variable2)

    return variable1



tools = include_all_tools_functions(TOOLS_FUNCTIONS)

add_enum_to_param(tools=tools,function_name="find_one_word_intent", param="intent", enum=["NEW", "UPDATE"])



def execute_function_from_prompt(chat_model, prompt, function_name, messages, model="llama3-70b-8192", temparature=0.3):
    
    chat_completion = chat_model.chat.completions.create(
        messages = messages,
        model=model,
        temperature=temparature,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": function_name}}
    )

    function_response = ""
    second_response = ""


    if chat_completion.choices[0].message.tool_calls:

        tool_calls = chat_completion.choices[0].message.tool_calls

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments
            function_args = json.loads(function_args)
            function = TOOLS_FUNCTIONS[function_name]['function']

            function_response = function_response + function(**function_args)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                }
            )

            second_response_ =  chat_model.chat.completions.create(
                model=model, messages=messages
            )

            
            second_response = second_response + second_response_.choices[0].message.content

    return (function_response, second_response)



def find_call_objective_for_agent(chat_model, agent, prompt ):
    messages = []
    messages.append(            {
             "role": "user",
                "content": prompt,
            }
    )
    messages.append ( {
        "role": "user", 
        "content": f"what is the objective of {agent} in above? "
    })


    (call_objective, response) = execute_function_from_prompt(
        chat_model=chat_model, prompt=prompt, function_name="call_objective", messages=messages)
    call_objective = json.loads(call_objective)
    call_objective = call_objective['call_objective']
    print(call_objective)
    return call_objective
    

def func_find_target_agents(chat_model, prompt):
    messages = []
    messages.append(            {
             "role": "user",
                "content": prompt,
            }
    ) 
        
    (target_agents, response) = execute_function_from_prompt(
        chat_model=chat_model, prompt=prompt, function_name="find_target_agents", messages=messages, temparature=0.2)
    
    

    target_agents = json.loads(target_agents)
    target_agents =     target_agents['target_agents']
    

    ret_target_agents = []
       
    if isinstance(target_agents, List): 
        for target_agent in target_agents : 
            print(target_agent)
    else :
        import re
        pattern = r',+'
            
        target_agents = re.split(pattern, target_agents)
    
        for target_agent in target_agents : 
            #print(target_agent)
            target_agent = re.sub("^\s?",'', target_agent)
            target_agent = re.sub("\w?\s?@",'', target_agent)
            target_agent = '@' + target_agent
            ret_target_agents.append(target_agent)
    return ret_target_agents
    





def process_system_prompt(chat_model, prompt):

    target_agents = func_find_target_agents(chat_model=chat_model, prompt=prompt)
    
    for target_agent in target_agents:
        call_objective = find_call_objective_for_agent(chat_model, target_agent, prompt)
        #one_word_intent = func_find_one_word_intent(chat_model, call_objective)
        print(target_agent)
        #print(f"{target_agent}: {one_word_intent} : {call_objective}")

def func_find_one_word_intent(chat_model, prompt):
    messages = []
    messages.append(            {
             "role": "user",
                "content": prompt,
            }
    ) 
        
    (response1, response2) = execute_function_from_prompt(
        chat_model=chat_model, prompt=prompt, function_name="find_one_word_intent", messages=messages)
    
#    print(response1)
#    print(response2)

    response1 = json.loads(response1)
    return response1['one_word_intent']


    

if __name__ == "__main__":
    while True:
        system_prompt = input("> ")
#        func_find_one_word_intent(chat_model=groq_chat, prompt=system_prompt)
        process_system_prompt(chat_model=groq_chat, prompt= system_prompt)

