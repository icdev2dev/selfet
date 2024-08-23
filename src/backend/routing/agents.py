import asyncio
import copy
import openai

from bmodels import get_agents as real_get_agents, get_agent_details
from butils import post_message
from flask import jsonify
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from bmodels.exceptions import APIException


from bmodels.assistants.asyncassistant import AsyncAssistant
from bmodels.assistants.autoexecassistant import AutoExecAssistant

ASSISTANT_WATCH_SLEEP_TIME = 5


def get_agents() : 
    return jsonify([{'name': x} for x in real_get_agents()])




async def run_assistant(assistant_id, entity_list, socketio): 
    
    assistant_async = AsyncAssistant(assistant_id=assistant_id, 
                                     entity_list=entity_list, 
                                     assistant_watch_sleep_time=ASSISTANT_WATCH_SLEEP_TIME,
                                     socketio=socketio
                                     )
    return await assistant_async()


@retry(
    stop=stop_after_attempt(3),  # Retry up to 5 times
    wait=wait_exponential(min=1, max=3),  # Exponential backoff starting from 1 second up to 10 seconds
    retry=retry_if_exception_type(APIException)  # Retry only on APIException
)

def watch_assistants(task_queue, entity_list, socketio):

        try:

            autoexecassistant_list = [assistant.id for assistant in AutoExecAssistant.list() if assistant.real_role == 'assistant']

            entity_set = set(entity_list)
            autoexecassistant_set = set(autoexecassistant_list)

            if len (autoexecassistant_set - entity_set) > 0 :
                for assistant in (autoexecassistant_set -entity_set) :
                    print(assistant) 
                    entity_list.append(assistant)

                    print(entity_list)
                    task_queue.append(asyncio.create_task(run_assistant(assistant_id=assistant, entity_list=entity_list, socketio=socketio)))
        
            entity_set_copy = copy.deepcopy(entity_set)

            if len (entity_set_copy - autoexecassistant_set) > 0:
                for assistant in (entity_set_copy - autoexecassistant_set) :
                    entity_list.remove(assistant)

        except APIException as e:
            raise e
        except (openai.APIConnectionError, openai.APITimeoutError) as e : 
            print("API Error in watch assistants")
            raise APIException from e

