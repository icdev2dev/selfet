import asyncio
import copy
import openai
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from bmodels.assistants.autoexecassistant import AutoExecAssistant
from bmodels.assistants.asyncassistant import AsyncAssistant

from bmodels.messages import post_message_on_subscription_channel

from bmodels.exceptions import APIException

from butils import list_subscription_threads, retrieve_subscription_thread, delete_subscription_message


def process_pub_msgs(assistant, st_msgs) :  
    for x in st_msgs:
        sqlish = x.content[0]['value']
        print(sqlish)
 #      assistant.process_sqlish(sqlish)




@retry(
    stop=stop_after_attempt(3),  # Retry up to 5 times
    wait=wait_exponential(min=1, max=3),  # Exponential backoff starting from 1 second up to 10 seconds
    retry=retry_if_exception_type(APIException)  # Retry only on APIException
)


def process_thread (assistant, thread, process_in_seq):
        try:
            limit = 3

            process_from_begin = False

            if thread.hwm == "":
                process_from_begin = True

            if process_from_begin == True:
                thread_msgs = thread.list_messages(limit=limit, order="asc")

                while len(thread_msgs) > 0:
                    after = thread_msgs[-1].id
                    process_in_seq(assistant, thread_msgs )
                    thread.set_hwm(after)

                    thread_msgs = thread.list_messages(limit=3, order="asc", after=after)

            else:
                process_thread_msgs = []
                conti = True
                thread_msgs = thread.list_messages(limit=limit)
                
                while len(thread_msgs) > 0 and conti == True :
                    for thread_msg in thread_msgs :
                        if (thread_msg.id != thread.hwm) : 
                            process_thread_msgs.append(thread_msg)
                        else:
                            conti = False
                            break
                    after = thread_msgs[-1].id
                    thread_msgs = thread.list_messages(limit=limit, after=after)
                                    
                if len(process_thread_msgs) != 0:
                    process_thread_msgs = process_thread_msgs[::-1]
                    process_in_seq(assistant, process_thread_msgs)
                    hwm = process_thread_msgs[-1].id
                    thread.set_hwm(hwm=hwm)
                else: 
                    pass
        except ( openai.APITimeoutError , openai.APIConnectionError) as e:
            print("API Error")
            raise APIException from e
            



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
                    print(top_message.content)

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
