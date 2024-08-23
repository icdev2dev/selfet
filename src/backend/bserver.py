import asyncio
import copy
import openai

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from bmodels.assistants.autoexecassistant import AutoExecAssistant
from bmodels.assistants.asyncassistant import AsyncAssistant
from bmodels.exceptions import APIException

from butils import  list_active_subscription_threads

from butils import update_system_counts
from butils import get_next_steps, process_next_steps


RESOURCEWATCHER_SLEEP_TIME = 10
ASSISTANT_WATCH_SLEEP_TIME = 5

def run_next_steps(list_messages, destination_thread_id):

    next_steps = get_next_steps(list_messages=list_messages)
    process_next_steps(next_steps=next_steps, destination_thread_id=destination_thread_id)




@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(min=1, max=3),  # Exponential backoff starting from 1 second up to 3 seconds
    retry=retry_if_exception_type(APIException)  # Retry only on APIException
)

def watch_subscription_threads(task_queue, subscription_thread_list):

    try: 
        sthread_list = list_active_subscription_threads()

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
                   run_next_steps(list_messages_, as_thread.id)

    except (openai.APIConnectionError, openai.APITimeoutError) as e : 
            print("API Error in watch subscription threads")
            raise APIException from e




async def run_assistant(assistant_id, entity_list): 
    assistant_async = AsyncAssistant(assistant_id=assistant_id, entity_list=entity_list, assistant_watch_sleep_time=ASSISTANT_WATCH_SLEEP_TIME)
    return await assistant_async()


@retry(
    stop=stop_after_attempt(3),  # Retry up to 5 times
    wait=wait_exponential(min=1, max=3),  # Exponential backoff starting from 1 second up to 10 seconds
    retry=retry_if_exception_type(APIException)  # Retry only on APIException
)

def watch_assistants(task_queue, entity_list):

        try:

            autoexecassistant_list = [assistant.id for assistant in AutoExecAssistant.list() if assistant.real_role == 'assistant']
        

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
        await asyncio.sleep(RESOURCEWATCHER_SLEEP_TIME)

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
