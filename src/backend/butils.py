import yaml



from bmodels.messages import AutoExecSubMessage
from bmodels.messages import AutoExecListenMessage

from bmodels.threads.sub import AutoExecSubThread


from bmodels import get_agents, get_agent_details, delete_all_registered_agents
from bmodels import create_registered_agents_from_yaml
from bmodels import list_registered_agents_in_registry as get_registered_agents

from bmodels import find_communication_channel_for_agent
from typing import List

def list_subscription_threads() -> List[AutoExecSubThread]:
    return [AutoExecSubThread.retrieve(thread_id=x.thread_id) for x in AutoExecSubThread.list()]

def create_subscription_thread() -> AutoExecSubThread:
    return AutoExecSubThread.create(originator="system")


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
    return AutoExecSubMessage.delete(thread_id=thread_id, message_id=message_id )


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

def send_request_to_agent(common_name, request): 

    communication_channel = find_communication_channel_for_agent(common_name=common_name)
    if communication_channel:
        post_message_on_communication_channel(communication_channel, request, class_type="user_request")


def post_message_on_communication_channel (communication_channel, request, class_type, originator="user"):

    destination_thread_id = AutoExecSubThread.list()[0].thread_id
    AutoExecListenMessage.create(thread_id=communication_channel, 
                                 content=request, 
                                 destination_thread_id= destination_thread_id, 
                                 class_type=class_type,
                                 originator=originator)



def post_message_on_subscription_channel(subscription_channel, request, originator) :
    from bmodels import AutoExecSubMessage
    AutoExecSubMessage.create(thread_id=subscription_channel, content=request, originator=originator)






