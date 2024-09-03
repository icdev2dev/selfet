import json
from typing import Annotated, List
import re

from bmodels.messages import AutoExecSubMessage
from bmodels.messages import AutoExecListenMessage

from bmodels.threads.sub import AutoExecSubThread
from bmodels.assistants.autoexecassistant import AutoExecAssistant, list_human_agents_in_registry, get_registered_agent_by_name



from tools_utils import tools_function, include_all_tools_functions

from bmodels import list_registered_agents_in_registry as get_registered_agents
from bmodels import delete_all_registered_agents
from bmodels import create_registered_agents_from_yaml


from bmodels import find_communication_channel_for_agent


from tools_utils import groq_chat
#from tools_utils import openai_chat as groq_chat



MODEL_N1 = "llama3-groq-8b-8192-tool-use-preview"
#MODEL_N1 = "llama3-groq-70b-8192-tool-use-preview"
#MODEL_N1 = "gpt-4o-mini"



############################### TOOLS ################################################

TOOLS_FUNCTIONS = {}

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
    return reworded_next_step


@tools_function(TOOLS_FUNCTIONS)
def next_step_for_agent ( sentence: Annotated[str, "The sentence should describes what the next step should be for me considering my relevant background in light of the conversation so far, why this next step is required and how to accomplish the next step. "]):
    """
    The conversation so far is carried out between different agents through different messages.

    Each message MAY have multiple target_agents and if it has a target agent, it MAY have source_agents. 
    ALL agents are explicity mentioned in the text; typically prefixed by '@'. 

    Pay SPECIFIC attention to the LAST BUT ONE MESSAGE as it, by and large, contains most clues to 
    what the next step could be. HOWEVER also look at ALL previous messages as they might also contain hidden 
    context that may not be visible in only the last message. 

    THE MAIN PURPOSE OF THE **ONE** SENTENCE IS TO PRODUCE THE NEXT STEP. What should I do? Make it specific 
    to **ME** and avoid general terms. 
    """


    data = {'action': sentence}
    return json.dumps(data)




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

############################### END TOOLS ################################################



def team_composition():
    TEAM_COMPOSITION = """The team consists of the following team members (aka agents)  
        along with their backgrounds.\n"""


    for r_a in get_registered_agents():
        r_a = json.loads(r_a)
        TEAM_COMPOSITION = TEAM_COMPOSITION + f"\n **{r_a['common_name']}** : \n"
        assistant = AutoExecAssistant.retrieve(assistant_id=r_a['id'])

        TEAM_COMPOSITION = TEAM_COMPOSITION + assistant.instructions

    return TEAM_COMPOSITION





############################### NEXT STEPS ################################################




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
            function_args = json.loads(function_args)
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
    



def process_next_steps(next_steps, destination_thread_id): 

    registered_agents = get_registered_agents()
    r_as = []

    for registered_agent in registered_agents:
        r_a = json.loads(registered_agent)
        r_as.append(r_a['common_name'])

    agents = []
    actions = []

    for next_step in next_steps:
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

                FUNCTION_NAME_2 = "reword_next_step_full_on"
                SYSTEM_MSG_2 = """YOu are an expert in English Language. """
                messages = []
                messages.append({'role': 'system', 'content': SYSTEM_MSG_2})
                messages.append({'role': 'user', 'content': next_step})


                chat_completion = groq_chat.chat.completions.create(
                    messages = messages,
                    model=MODEL_N1,
                    tools=tools,
                    temperature=0.01,
                    tool_choice={"type": "function", "function": {"name": FUNCTION_NAME_2}}
                )

                if chat_completion.choices[0].message.tool_calls:
                        tool_call = chat_completion.choices[0].message.tool_calls[0]
                        function_name = tool_call.function.name

                        if function_name == FUNCTION_NAME_2:
                            
                            function_args = tool_call.function.arguments
                            function_args = json.loads(function_args)
                            print(f"{next_step} -> {function_args}");
                            actions.append(function_args['reworded_next_step'])
    
        for agent, action in zip(agents, actions):

            print(agent, call_reword_next_step(action))
            send_request_to_agent_with_destination_thread_id(agent, call_reword_next_step(action), destination_thread_id=destination_thread_id)

    else:
        for agent, action in zip(agents, actions):
            print(agent, call_reword_next_step(action))
            send_request_to_agent_with_destination_thread_id(agent, call_reword_next_step(action), destination_thread_id=destination_thread_id)



def what_should_individual_agents_do(content) : 
    FUNCTION_NAME = "next_step_for_agent" 


    for r_a in get_registered_agents():
        messages=[]

        r_a = json.loads(r_a)
        name = r_a['common_name']
        assistant = AutoExecAssistant.retrieve(assistant_id=r_a['id'])
        background = assistant.instructions

            
        NEXT_STEP_SYSTEM_MESSAGE = f"""
        You are **{name}**. 
        **Background**:  
        {background}.

        You should word the request in the first person in form of one sentence. The request should be **ONLY** focussed on proposed action without any 
        background information of why it is required. It is understood that others will understand why you are making the
         request. In this way the sentence will be pithy It **should** be only one sentence.
        """

#        print(NEXT_STEP_SYSTEM_MESSAGE)

        messages.append({'role': 'system', 'content': NEXT_STEP_SYSTEM_MESSAGE})
        messages.append({'role': 'user', 'content': content})


        chat_completion = groq_chat.chat.completions.create(
            messages = messages,
            model=MODEL_N1,
            tools=tools,
            temperature=0.5,
            tool_choice={"type": "function", "function": {"name": FUNCTION_NAME}}
        )

        if chat_completion.choices[0].message.tool_calls:
            next_steps = []
            tool_calls = chat_completion.choices[0].message.tool_calls


            tool_call = tool_calls[0]

            function_name = tool_call.function.name
            if function_name == FUNCTION_NAME:
                    
                    function_args = tool_call.function.arguments
                    function_args = json.loads(function_args)
                    print(f"{name}-----> {function_args}")




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
    
    content = ""

    for x in list_messages:
        content = content + x

    what_should_individual_agents_do(content)

    messages.append({'role': 'user', 'content': content})
    
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

        
        return next_steps







############################## END  NEXT STEPS ############################################


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


def list_threads_by_active_status(active_status="Y") -> List[AutoExecSubThread]:

    active_subscription_threads = []

    for x in AutoExecSubThread.list():
        y = AutoExecSubThread.retrieve(thread_id=x.thread_id)
        if y.is_active == active_status:
            active_subscription_threads.append(y)
    return active_subscription_threads


def list_active_subscription_threads() -> List[AutoExecSubThread]:
    return list_threads_by_active_status()

def list_inactive_subscription_threads() -> List[AutoExecSubThread]:
    return list_threads_by_active_status("N")



def purge_inactive_subscription_threads() : 
    inactive_subthreads = list_threads_by_active_status("N")
    for inactive_subthread in inactive_subthreads:
        AutoExecSubThread.delete(inactive_subthread.id)


def list_subscription_threads() -> List[AutoExecSubThread]:
    return [AutoExecSubThread.retrieve(thread_id=x.thread_id) for x in AutoExecSubThread.list()]

def create_subscription_thread(**kwargs) -> AutoExecSubThread:
    return AutoExecSubThread.create(**kwargs, originator="system")


def retrieve_subscription_thread(thread_id) -> AutoExecSubThread:
    return AutoExecSubThread.retrieve(thread_id=thread_id)



def get_conversation_history(index:int=0):
    subscription_threads = list_subscription_threads()
    if len(subscription_threads) > index:
        subscription_thread = subscription_threads[index]
        messages = subscription_thread.list_messages(limit=100, order="asc")
        for message in messages:
            if message.originator == "system_counts":
                pass
            else:
                print(f"********************** {message.originator}***********************")
                print(f"{message.content[0]['text'].value}")





def delete_subscription_message(thread_id, message_id):
    import openai
    try : 
        AutoExecSubMessage.delete(thread_id=thread_id, message_id=message_id )
    except openai.NotFoundError as e:
        pass
    


def delete_last_message_in_subscription_thread(index:int=0):
    subscription_threads = list_subscription_threads()
    if len(subscription_threads) > index:
        subscription_thread = subscription_threads[index]
        messages = subscription_thread.list_messages()
        if len(messages) > 0 :
            message = messages[-1]
            delete_subscription_message(thread_id=subscription_thread.id, message_id=message.id)


def delete_last_message_in_subscription_thread_from_agent(agent_name, index:int=0):
    pass


def delete_all_subscription_threads():

    as_threads = AutoExecSubThread.list()
    print(as_threads)
    for as_thread in as_threads:
        AutoExecSubThread.delete(thread_id=as_thread.thread_id)
    print(AutoExecSubThread.list())


def send_request_to_agent_with_destination_thread_id(common_name, request, destination_thread_id ):

    communication_channel = find_communication_channel_for_agent(common_name=common_name)

    if communication_channel:
        post_message_on_communication_channel(communication_channel, request, class_type="user_request", destination_thread_id=destination_thread_id, originator=common_name)


def send_request_to_agent(common_name, request, index=0): 

    active_sub_threads = list_active_subscription_threads()

    if len(active_sub_threads) > index:
        destination_thread_id = active_sub_threads[index].id
        send_request_to_agent_with_destination_thread_id(common_name, request, destination_thread_id )



def post_message_on_communication_channel (communication_channel, request, class_type, destination_thread_id, originator="user"):

    AutoExecListenMessage.create(thread_id=communication_channel, 
                                    content=request, 
                                    destination_thread_id= destination_thread_id, 
                                    class_type=class_type,
                                    originator=originator)
    
def post_message(request, originator, index:int=0):
    subscription_threads = list_subscription_threads()
    if len(subscription_threads) > index:
        subscription_channel = subscription_threads[index].id
        post_message_on_subscription_channel(subscription_channel=subscription_channel, request=request, originator=originator)    


def post_message_on_subscription_channel(subscription_channel, request, originator) :    
    AutoExecSubMessage.create(thread_id=subscription_channel, content=request, originator=originator)

