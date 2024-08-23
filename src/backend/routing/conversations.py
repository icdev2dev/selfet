from typing import List

from butils import list_active_subscription_threads, list_inactive_subscription_threads
from butils import create_subscription_thread

from butils import purge_inactive_subscription_threads

from butils import AutoExecSubThread
from butils import list_active_subscription_threads as active_conversations
from butils import update_system_counts
from butils import get_next_steps, process_next_steps
from bserver import APIException
import openai

from flask import jsonify, request
from flask_socketio import emit

import asyncio
import random, copy

CONVERSATION_WATCHER_SLEEP_TIME = 15

CONVERSATIONS = []


class AsyncConversation:
    def __init__(self, id, conversation_watch_sleep_time, socketio) -> None:
        self.conversation_watch_sleep_time = conversation_watch_sleep_time
        self.id = id
        self.socketio = socketio

    async def __call__(self) :
        try: 
            while True:

                as_thread = AutoExecSubThread.retrieve(self.id)

                list_messages = as_thread.list_messages(limit=100)

                if int(as_thread.max_msgs_on_thread) < len(list_messages):
                    as_thread.is_active = "N"
                    as_thread.generic_update_metadata()
                    print("Set Thread as inactive")
                    a = self.socketio.emit('madeConversationInactive', {})                    
                    print(a)

                elif as_thread.conversation_type == "MMA":
                    pass
                elif len(list_messages) > 0:
                    top_message = list_messages[0]
                    
                    if top_message.originator != "system_counts":
                        update_system_counts(thread_id=as_thread.id, list_messages=list_messages)
                    else:
                        list_messages_ = []

                        for x in reversed(list_messages):
                                list_messages_.append(f"\n---------------{x.originator}---------------\n{x.content[0]['text'].value} \n --------------------------------------------------\n")

                        next_steps = get_next_steps(list_messages=list_messages_)
                        process_next_steps(next_steps=next_steps, destination_thread_id=self.id)
                await asyncio.sleep(self.conversation_watch_sleep_time)

        except (openai.APIConnectionError, openai.APITimeoutError) as e : 
            print("API Error in watch subscription threads")
            raise APIException from e
        
        except asyncio.CancelledError as ce:
            print(f"Conversation with id {self.id} was cancelled")
            raise ce


async def monitor_conversation(id, conversation_watch_sleep_time, socketio ): 
    conversation_async = AsyncConversation(id, conversation_watch_sleep_time, socketio)
    return await conversation_async()


async def f_active_conversations(conversations:List): 
    global CONVERSATIONS

    a_c_t = [x.id for x in active_conversations()]

    await asyncio.sleep(0) # simulate real sync work
    CONVERSATIONS =  copy.deepcopy(a_c_t)


async def watch_conversations(task_watcher:List, task_queue:List, conversations:List, socketio):

    global CONVERSATIONS

    prev_conversations = copy.deepcopy(CONVERSATIONS)
    await f_active_conversations(conversations=conversations)
    
    conversations = copy.deepcopy(CONVERSATIONS)


    if len(set(conversations) - set(prev_conversations)) > 0 :
        ## Need to add 
        for id in (set(conversations) - set(prev_conversations)):
            conversation_watcher_task = asyncio.create_task( monitor_conversation(id, CONVERSATION_WATCHER_SLEEP_TIME, socketio))
            task_watcher.append({'type': 'conversation', 'id': id, 'task': conversation_watcher_task })
            task_queue.append(conversation_watcher_task)


    elif len(set(prev_conversations) - set(conversations)) > 0:
        ## Need to delete        
        pos = []
        for id in (set(prev_conversations) - set(conversations)): 
            for index, task in enumerate(task_watcher):  
                if task['type'] == 'conversation' and task['id'] == id:
                    pos.append(index)

        print(pos)

        if len(pos) > 0: 
            for i in pos:
                task_watcher[i]['task'].cancel()

            deleted = 0
            for i in pos: 
                del task_watcher[i-deleted]
                deleted = deleted + 1            
    print(task_watcher[0]['task'])

    print(task_queue)
    
    print(f"Updated Task Watcher: {task_watcher}")

    for i in range(1,len(task_watcher)):
        task = task_watcher[i]
        if task['task'].done():
            print(f"{task['id']} is done")
        elif task['task'].cancelled():
            print(f"{task['id']} was cancelled")




def delete_all_inactive_conversations() :
    purge_inactive_subscription_threads()
    return jsonify("ok")


def get_active_conversations() :
    return jsonify( [{'id': x.id, 'name': x.name} for x in  list_active_subscription_threads()])

def get_inactive_conversations() :
    return jsonify( [{'id': x.id, 'name': x.name} for x in  list_inactive_subscription_threads()])

def create_conversation():
    data = request.get_json()
    name = data.get('name')
    max_msgs_on_thread = str(data.get('max_msgs_on_thread'))

    
    create_subscription_thread(name=name, max_msgs_on_thread=max_msgs_on_thread)
    return jsonify("ok")

def set_conversation_type():
    data = request.get_json()
    thread_id = data.get('thread_id')
    conversation_type = data.get('conversation_type')
    aest = AutoExecSubThread.retrieve(thread_id=thread_id)
    aest.set_conversation_type(conversation_type=conversation_type)
    return jsonify("ok")



def get_conversation(conversationId:str):
    ret_val = {
    }
    aest = AutoExecSubThread.retrieve(thread_id=conversationId)
    conversation_name = aest.name
    conversation_type = aest.conversation_type

    max_msgs_on_thread = aest.max_msgs_on_thread

    list_messages = aest.list_messages(order='asc')
    num_of_msgs_on_thread = len(list_messages)
    
    ret_val['conversation_name'] = conversation_name
    ret_val['conversation_type'] = conversation_type
    
    ret_val['max_msgs_on_thread'] = max_msgs_on_thread
    ret_val['num_of_msgs_on_thread'] = num_of_msgs_on_thread

    msgs_by_author = {}
    msgs = []
    for msg in list_messages:

        msgs.append({'originator': msg.originator, 'text': msg.content[0]['text'].value})

    ret_val['msgs'] = msgs

    for msg in list_messages:
        if msg.originator not in msgs_by_author.keys():
            msgs_by_author[msg.originator] = 1
        else:
            msgs_by_author[msg.originator] = msgs_by_author[msg.originator] + 1

    ret_val['msgs_by_author'] = ''

    for author, cnt in msgs_by_author.items():
        ret_val['msgs_by_author'] =     ret_val['msgs_by_author'] + author + " : " + str(cnt) + " \n"
        
    return jsonify(ret_val)





