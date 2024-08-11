import asyncio
import copy
import openai
import json
import re

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Annotated

from bmodels.assistants.autoexecassistant import AutoExecAssistant, list_registered_agents_in_registry as get_registered_agents

from bmodels.assistants.asyncassistant import AsyncAssistant

from bmodels.messages import post_message_on_subscription_channel

from bmodels.exceptions import APIException

from butils import list_subscription_threads, retrieve_subscription_thread, delete_subscription_message
from butils import send_request_to_agent

from tools_utils import tools_function, include_all_tools_functions

#from tools_utils import openai_chat as groq_chat
from tools_utils import groq_chat


#MODEL_N1 = "llama3-groq-70b-8192-tool-use-preview"
MODEL_N1 = "llama3-groq-8b-8192-tool-use-preview"

#MODEL_N1 = "gpt-4o-mini"

TOOLS_FUNCTIONS = {}




def process_pub_msgs(assistant, st_msgs) :  
    for x in st_msgs:
        sqlish = x.content[0]['value']
        print(sqlish)
 #      assistant.process_sqlish(sqlish)


def more_than_one_author(sentence) -> bool:
    return True


def is_sentence_compound(sentence) -> bool:

    if len(sentence) > 70 and more_than_one_author(sentence=sentence):
        return True
    else: 
        return False
    



@tools_function(TOOLS_FUNCTIONS)
def assign_agent(agent: Annotated[str, "The agent who should get this task based on the background of the team member"]):
    """
    This function picks the team member as the agent who should get this task. The ideal team member is the one who 
    best meets what the task entails; given the diverse background of team members. In certain cases two team members 
    might have nearly the same qualities; in which additional attention must be paid to every word of the backrgound.
    """
    print(assign_agent)




@tools_function(TOOLS_FUNCTIONS)
def reword_next_step_full_on(reworded_next_step: Annotated[str, "The reworded_next_step should describe the message IN TEXT as a request in second person; rephrased as a question"]):
    """
    This function describes the message as text; reworded as a question in second person. The task of this function 
    is to reword the sentence as if refering to the main subject in abstact.

    i.e. "should carry on" would become "could you please carry on?"

        Each message MAY have multiple target_agents and if it has a target agent, it MAY have source_agents. TOTALLY 
    REFRAIN FROM INCLUDING TARGET_AGENTS AND SOURCE_AGENTS. ALL agents are explicity mentioned in the text; 
    typically prefixed by '@'. The distinction between the two types of agents is VERY important. The target agent 
    can be thought about as the subject in advait vedanta and the source agent is the object in adavit vedanta. 
    The text is always requesting the target agent to do something. The source agent may make further references 
    to other agents. 

    The reworded_next_step should **NOT** contain any mention of any agent.
    
    """

@tools_function(TOOLS_FUNCTIONS)
def reword_next_step(reworded_next_step: Annotated[str, "The reworded_next_step should describe the message IN TEXT as a request in second person; rephrased as a question"]):
    """
    The message describes a part of the entire sentence where the main subject is cut out. The task of this function 
    is to reword the part of the sentence as if refering to the main subject in abstact.

    i.e. "should carry on" would become "could you please carry on?"


    """
#    print(reworded_next_step)
    return reworded_next_step



@tools_function(TOOLS_FUNCTIONS)
def next_step ( sentence: Annotated[str, "The sentence should describes what the next step should be in light of the conversation so far, why this next step is required and how to accomplish the next step. "]):
    """
    The conversation so far is carried out between different agents through different messages.

    Each message MAY have multiple target_agents and if it has a target agent, it MAY have source_agents. TOTALLY 
    REFRAIN FROM INCLUDING TARGET_AGENTS AND SOURCE_AGENTS. ALL agents are explicity mentioned in the text; 
    typically prefixed by '@'. The distinction between the two types of agents is VERY important. The target agent 
    can be thought about as the subject in advait vedanta and the source agent is the object in adavit vedanta. 
    The text is always requesting the target agent to do something. The source agent may make further references 
    to other agents. 

    Pay SPECIFIC attention to the LAST BUT ONE MESSAGE as it, by and large, contains most clues to what the next step could be. 
    HOWEVER also look at previous messages as they might also contain hidden context that may not be visible in only 
    the last message. 

    THE MAIN PURPOSE OF THE **ONE** SENTENCE IS TO PRODUCE THE NEXT STEP. WHAT SHOULD THE AGENT DO NEXT. BE SPECIFIC WHILE TARGETING AN AGENT. 
    WHAT IS THE ACTION ITEM FOR THE AGENT IS THE QUESTION TO ANSWER. MAKE IT SPECIFIC TO ONE AGENT. AVOID GENERAL TERMS.
    """


    data = {'action': sentence}
    return json.dumps(data)


tools = include_all_tools_functions(TOOLS_FUNCTIONS)




def call_reword_next_step(next_step):
    messages=[]
    REWORD_NEXT_STEP_SYSTEM_MESSAGE = """
    You are grammatical expert. You know how to reword sentences according to what the request is.
    """
    FUNCTION_NAME = "reword_next_step"


    messages.append({'role': 'system', 'content': REWORD_NEXT_STEP_SYSTEM_MESSAGE})
    messages.append({'role': 'user', 'content': next_step})
    

    chat_completion = groq_chat.chat.completions.create(
        messages = messages,
        model=MODEL_N1,
        tools=tools,
        temperature=0.01,
        tool_choice={"type": "function", "function": {"name": FUNCTION_NAME }}
    )

    if chat_completion.choices[0].message.tool_calls:

        tool_calls = chat_completion.choices[0].message.tool_calls
        tool_call = tool_calls[0]


        function_name = tool_call.function.name


        if function_name == FUNCTION_NAME:
            function_args = tool_call.function.arguments

#            print(function_args)
            function_args = json.loads(function_args)

#            print(function_args)
#            print(type(function_args))

            real_function_args = {}

            if type(function_args) == dict:
                for k,v in function_args.items():
                    real_function_args['reworded_next_step'] = v
                    break
            else:
                real_function_args = function_args

            function = TOOLS_FUNCTIONS[function_name]['function']

            function_response = function(**real_function_args)
            return function_response
    



def process_next_steps(next_steps): 

    registered_agents = get_registered_agents()
    r_as = []

    for registered_agent in registered_agents:
        r_a = json.loads(registered_agent)
        r_as.append(r_a['common_name'])

    agents = []
    actions = []


    for next_step in next_steps:
#        print(next_step)
        for ra in r_as: 
            m = re.match(ra, next_step)
            if m :  
                if m.span()[0] == 0:
                    agents.append(ra)
                    actions.append(re.split(ra, next_step)[1])
                    break

    if len(actions) == 0 and len(next_steps) != 0:
        TEAM_COMPOSITION = """The team consists of the following team members  
            along with their backgrounds.\n"""


        for r_a in get_registered_agents():
            r_a = json.loads(r_a)
            TEAM_COMPOSITION = TEAM_COMPOSITION + f"\n {r_a['common_name']} : "
            assistant = AutoExecAssistant.retrieve(assistant_id=r_a['id'])

            TEAM_COMPOSITION = TEAM_COMPOSITION + assistant.instructions

        content = ""

        for next_step in next_steps:
            content = content + " " + next_step

        SYSTEM_MSG = """You are an expert judge of which team member is best suited for the task at hand. You look at the
        background of each team member to make the determination. """
        messages = []
        messages.append({'role': 'system', 'content': SYSTEM_MSG+TEAM_COMPOSITION})
        messages.append({'role': 'user', 'content': content})


        FUNCTION_NAME = "assign_agent"

        chat_completion = groq_chat.chat.completions.create(
            messages = messages,
            model=MODEL_N1,
            tools=tools,
            temperature=0.01,
            tool_choice={"type": "function", "function": {"name": FUNCTION_NAME}}
        )

        if chat_completion.choices[0].message.tool_calls:
            tool_call = chat_completion.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name

            if function_name == FUNCTION_NAME:
                
                function_args = tool_call.function.arguments
                function_args = json.loads(function_args)
#                    print(f"{next_step} -> {function_args['agent']}");

                agents.append(function_args['agent'])

                FUNCTION_NAME = "reword_next_step_full_on"
                SYSTEM_MSG = """YOu are an expert in English Language. """
                messages = []
                messages.append({'role': 'system', 'content': SYSTEM_MSG})
                messages.append({'role': 'user', 'content': next_step})


                chat_completion = groq_chat.chat.completions.create(
                    messages = messages,
                    model=MODEL_N1,
                    tools=tools,
                    temperature=0.01,
                    tool_choice={"type": "function", "function": {"name": FUNCTION_NAME}}
                )

                if chat_completion.choices[0].message.tool_calls:
                        tool_call = chat_completion.choices[0].message.tool_calls[0]
                        function_name = tool_call.function.name

                        if function_name == FUNCTION_NAME:
                            
                            function_args = tool_call.function.arguments
                            function_args = json.loads(function_args)
                            print(f"{next_step} -> {function_args}");
                            actions.append(function_args['reworded_next_step'])
    
        for agent, action in zip(agents, actions):

            print(agent, call_reword_next_step(action))
            send_request_to_agent(agent, call_reword_next_step(action))

    else:
        for agent, action in zip(agents, actions):
            print(agent, call_reword_next_step(action))
            send_request_to_agent(agent, call_reword_next_step(action))


def team_composition():
    TEAM_COMPOSITION = """The team consists of the following team members (aka agents)  
        along with their backgrounds.\n"""


    for r_a in get_registered_agents():
        r_a = json.loads(r_a)
        TEAM_COMPOSITION = TEAM_COMPOSITION + f"\n **{r_a['common_name']}** : \n"
        assistant = AutoExecAssistant.retrieve(assistant_id=r_a['id'])

        TEAM_COMPOSITION = TEAM_COMPOSITION + assistant.instructions

    return TEAM_COMPOSITION





def get_next_steps(list_messages):
    messages=[]
    NEXT_STEP_SYSTEM_MESSAGE = """
    You are very attuned to ANY conversation to see the genesis of the conversation as well as through your vast 
    data bank of different types of conversations, knowing where this conversation should go. This
    is usually based in the past of the conversation. But you are also the future seer of this conversation, you will
    predict how to steer the conversation. 

    Your job is to state what the next step is for each agent, as a suggestion of what potential participants 
    (aka agents) might take in a conversation. You **will** name an agent along with the task.  You understand that 
    it is possible that some agents will not have next steps in the conversation ATM.   
    
    You do think hard about what an agent should do next. You do have clarity to have a **single** sentence targeted for 
    a agent WORDED in the future tense. You **DO** look into the content of the each message to see if the author 
    is requesting help from other team members. 

    You do call out agent's name explicitly. 
    """

    FUNCTION_NAME = "next_step"

    messages.append({'role': 'system', 'content': NEXT_STEP_SYSTEM_MESSAGE + team_composition()})
#    print(messages)
    
    content = ""

    for x in list_messages:
        content = content + x

    
    messages.append({'role': 'user', 'content': content})
 #   print(messages)
    


    chat_completion = groq_chat.chat.completions.create(
        messages = messages,
        model=MODEL_N1,
        tools=tools,
        temperature=0.01,
        tool_choice={"type": "function", "function": {"name": FUNCTION_NAME}}
    )

    if chat_completion.choices[0].message.tool_calls:
        next_steps = []
        tool_calls = chat_completion.choices[0].message.tool_calls



        for tool_call in tool_calls:
            function_name = tool_call.function.name
            if function_name == FUNCTION_NAME:
                
                function_args = tool_call.function.arguments
                function_args = json.loads(function_args)
                function = TOOLS_FUNCTIONS[function_name]['function']
                function_response = function(**function_args)
                function_response = json.loads(function_response)
                function_response = re.split(r"\.", function_response['action']) 

                if len(function_response) == 1 or (len(function_response) == 2 and function_response[1] == ""):
                    next_steps.append(function_response[0])
                elif function_response[-1] == "":
                    for action in function_response[:-1]:
                        next_steps.append(action)
                else: 
                    for action in function_response:
                        next_steps.append(action)
#        print(f"next steps from get_next_steps : {next_steps}")
        return next_steps



def run_next_steps(list_messages):

    next_steps = get_next_steps(list_messages=list_messages)
    process_next_steps(next_steps=next_steps)



async def run_assistant(assistant_id, entity_list): 
    assistant_async = AsyncAssistant(assistant_id=assistant_id, entity_list=entity_list)

    return await assistant_async()


def update_system_counts(thread_id, list_messages):
    originator_msgs = {}
    system_msgs = []

    print("update system count")

    for msg in list_messages:
        originator = msg.originator

        if originator == "system_counts":
            system_msgs.append(msg.id)
        else:
            if originator != "":
                if originator not in originator_msgs.keys():
                    originator_msgs[originator] = 1
                else: 
                    originator_msgs[originator] = originator_msgs[originator] + 1

    for msg in system_msgs:
        delete_subscription_message(thread_id=thread_id, message_id=msg)

    post_message_on_subscription_channel(thread_id, 
                                        f"Number of posts : {json.dumps(originator_msgs)}" , 
                                        "system_counts" )










@retry(
    stop=stop_after_attempt(3),  # Retry up to 5 times
    wait=wait_exponential(min=1, max=3),  # Exponential backoff starting from 1 second up to 10 seconds
    retry=retry_if_exception_type(APIException)  # Retry only on APIException
)






def watch_subscription_threads(task_queue, subscription_thread_list):


    try: 
        sthread_list = list_subscription_threads()

        for thread in sthread_list:
            as_thread = thread

            list_messages = as_thread.list_messages(limit=100)

            if len(list_messages) > 0:
                top_message = list_messages[0]
                
                if top_message.originator != "system_counts":

                    update_system_counts(thread_id=as_thread.id, list_messages=list_messages)
                else:
                   list_messages_ = []

                   for x in reversed(list_messages):
                        list_messages_.append(f"\n---------------{x.originator}---------------\n{x.content[0]['text'].value} \n --------------------------------------------------\n")
                   run_next_steps(list_messages_)



    except (openai.APIConnectionError, openai.APITimeoutError) as e : 
            print("API Error in watch subscription threads")
            raise APIException from e

    




@retry(
    stop=stop_after_attempt(3),  # Retry up to 5 times
    wait=wait_exponential(min=1, max=3),  # Exponential backoff starting from 1 second up to 10 seconds
    retry=retry_if_exception_type(APIException)  # Retry only on APIException
)



def watch_assistants(task_queue, entity_list):

        try:

            autoexecassistant_list = [assistant.id for assistant in AutoExecAssistant.list()]
        

            entity_set = set(entity_list)
            autoexecassistant_set = set(autoexecassistant_list)

            if len (autoexecassistant_set - entity_set) > 0 :
                for assistant in (autoexecassistant_set -entity_set) : 
                    entity_list.append(assistant)
                    task_queue.append(asyncio.create_task(run_assistant(assistant_id=assistant, entity_list=entity_list)))
        
            entity_set_copy = copy.deepcopy(entity_set)

            if len (entity_set_copy - autoexecassistant_set) > 0:
                for assistant in (entity_set_copy - autoexecassistant_set) :
                    entity_list.remove(assistant)

        except APIException as e:
            raise e
        except (openai.APIConnectionError, openai.APITimeoutError) as e : 
            print("API Error in watch assistants")
            raise APIException from e




async def resource_watcher(task_queue, entity_list, subscription_thread_list ):

    while True:
        print("now in resource watcher")
        watch_assistants(task_queue, entity_list)
        watch_subscription_threads(task_queue, subscription_thread_list)
        await asyncio.sleep(60)

        


async def main():
    task_queue = []
    entity_list = []
    subscription_thread_list = []


    resource_watcher_task = asyncio.create_task (resource_watcher(task_queue=task_queue, 
                                                                  entity_list=entity_list,
                                                                  subscription_thread_list=subscription_thread_list
                                                                  ))
    task_queue.append(resource_watcher_task)
    await asyncio.gather(*task_queue)

def run_main():
    asyncio.run(main=main())


if __name__ == "__main__":
    run_main()
