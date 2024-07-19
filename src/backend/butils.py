import yaml

from bmodels import AutoExecAssistant
from bmodels import AutoExecListenMessage, AutoExecSubThread

from bmodels.assistants import list_registered_agents_in_registry as list_registered_agents
from bmodels import create_registered_agent_by_name as create_registered_agent, delete_registered_agent_by_name as delete_registered_agent

from bmodels import create_registered_agents_from_yaml, delete_all_registered_agents
from bmodels.messages import AutoExecSubMessage




from bmodels import find_communication_channel_for_agent
from typing import List

def list_subscription_threads() -> List[AutoExecSubThread]:
    return AutoExecSubThread.list()

def create_subscription_thread() -> AutoExecSubThread:
    return AutoExecSubThread.create()

def retrieve_subscription_thread(thread_id) -> AutoExecSubThread:
    return AutoExecSubThread.retrieve(thread_id=thread_id)

def delete_subscription_message(thread_id, message_id):
    return AutoExecSubMessage.delete(thread_id=thread_id, message_id=message_id )


def delete_all_subscription_threads(): 
    as_threads = AutoExecSubThread.list()
    print(as_threads)
    for as_thread in as_threads:
        AutoExecSubThread.delete(thread_id=as_thread.thread_id)
    print(AutoExecSubThread.list())

def send_request_to_agent(common_name, request): 
    communication_channel = find_communication_channel_for_agent(common_name=common_name)
    if communication_channel:
        post_message_on_communication_channel(communication_channel, request)


def post_message_on_communication_channel (communication_channel, request):

    destination_thread_id = AutoExecSubThread.list()[0].thread_id
    AutoExecListenMessage.create(thread_id=communication_channel, 
                                 content=request, 
                                 destination_thread_id= destination_thread_id)



def post_message_on_subscription_channel(subscription_channel, request, originator) :
    from bmodels import AutoExecSubMessage
    AutoExecSubMessage.create(thread_id=subscription_channel, content=request, originator=originator)






