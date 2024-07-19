import asyncio
import copy
import openai
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from bmodels import AutoExecAssistant, AutoExecListenThread, AutoExecSubThread

from tools_utils import groq_chat, openai_chat
from butils import list_registered_agents, post_message_on_subscription_channel


GENERAL_COMMUNICATION_STYLE = """
Please introduce yourself at the start of every messaage; so that others know who you are as well as
be able to respond back to you. Please prefix with '@'. You may give a relevant background if you feel like it. 
Even in your description, please prefix with '@' on your name. 

Also others will also use the same format 
to identify themselves. Therefore you can respond to messages in a personalized way; if the 
situation calls for it. Obviously when you refer to others in the team, you should also prefix 
their names with a '@'
"""

def team_composition(): 
    TEAM_COMPOSITION = """Your team consists of the following team members (including you) 
    along with their backgrounds.\n"""


    for r_a in list_registered_agents():
        r_a = json.loads(r_a)
        TEAM_COMPOSITION = TEAM_COMPOSITION + f"\n {r_a['common_name']} : "
        assistant = AutoExecAssistant.retrieve(assistant_id=r_a['id'])

        TEAM_COMPOSITION = TEAM_COMPOSITION + assistant.instructions

    TEAM_COMPOSITION = TEAM_COMPOSITION + """You may ask for feedback from others on the team; if relevant. 
    You don't have to. However whenever someone asks you to ask your team members, you MUST ONLY use the 
    team mates mentioned above. Once again you are not obliged to call on your team members if you don't feel
    like it.
    """
    return TEAM_COMPOSITION


def process_pub_msgs(assistant, st_msgs) :  
    for x in st_msgs:
        sqlish = x.content[0]['value']
        print(sqlish)
 #      assistant.process_sqlish(sqlish)

def process_listen_msgs(assistant, thread_msgs,chat_model = openai_chat, model="gpt-4o-mini") :

    name = assistant.name

    for thread_msg in thread_msgs:
        class_type = thread_msg.class_type

        destination_thread_id = thread_msg.destination_thread_id
        print(destination_thread_id)
        as_thread = AutoExecSubThread.retrieve(thread_id=destination_thread_id)

        previous_messages = []

        for message in as_thread.list_messages():
            previous_messages.append({'role': message.role, 'content': message.content[0]['text'].value})
        
        print(previous_messages)


        prompt = thread_msg.content[0]['text'].value

        messages=[]
        
        messages.append ({'role': 'system',
                          "content": f"You are {name}. \n" 
                        })        
        messages.append ({'role': 'system',
                          "content": assistant.instructions 
                        })
        messages.append ({'role': 'system',
                          "content": GENERAL_COMMUNICATION_STYLE 
                        })
        messages.append ({'role': 'system',
                          "content": team_composition() 
                        })
        
        for message in previous_messages:
            messages.append(message)


        messages.append({'role': 'user', 
                         'content': prompt   
                         })


        second_response = chat_model.chat.completions.create(
                model=model, messages=messages
            )

        print("\n\nSecond LLM Call Response:", second_response.choices[0].message.content)

        post_message_on_subscription_channel(destination_thread_id, second_response.choices[0].message.content, name )

class APIException(Exception):
    pass 




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
                    print("batch")
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
            



@retry(
    stop=stop_after_attempt(3),  # Retry up to 5 times
    wait=wait_exponential(min=1, max=3),  # Exponential backoff starting from 1 second up to 10 seconds
    retry=retry_if_exception_type(APIException)  # Retry only on APIException
)

async def monitor_assistant(assistant_id, entity_list):

    while True:
        print (f"from moni {assistant_id} ->  {entity_list}")

        if assistant_id not in entity_list:
            break
        else : 
            try : 
                autoexecassistant = AutoExecAssistant.retrieve(assistant_id=assistant_id)
                listen_thread = AutoExecListenThread.retrieve(thread_id=autoexecassistant.listen_thread)
                process_thread (autoexecassistant, listen_thread, process_listen_msgs)
#            pub_thread  = StreamThread.retrieve(thread_id=autoexecassistant.pub_thread)
#            process_thread (autoexecassistant, pub_thread, process_pub_msgs)
            

            except openai.NotFoundError as e:
                print(f"{e}")
                break
            except ( openai.APITimeoutError , openai.APIConnectionError) as e:
                print("API Error")
                raise APIException from e
            

        await asyncio.sleep(10)




def watch_subscription_threads(task_queue, subscription_thread_list):
    try: 
        from butils import list_subscription_threads, retrieve_subscription_thread, delete_subscription_message

        sthread_list = list_subscription_threads()


# post_message_on_subscription_channel(destination_thread_id, second_response.choices[0].message.content, name )

        for thread in sthread_list:
            as_thread = retrieve_subscription_thread(thread.thread_id)

            originator_msgs = {}
            system_msgs = []

            list_messages = as_thread.list_messages(limit=100)
            for msg in list_messages:
                originator = msg.originator

                if originator == "system_counts":
                    print(msg.content)
                    system_msgs.append(msg.id)
                else:
                    if originator not in originator_msgs.keys():
                        originator_msgs[originator] = 1
                    else: 
                        originator_msgs[originator] = originator_msgs[originator] + 1

            for msg in system_msgs:
                delete_subscription_message(thread_id=as_thread.id, message_id=msg)

            post_message_on_subscription_channel(as_thread.id, 
                                                 f"Number of posts : {json.dumps(originator_msgs)}" , 
                                                 "system_counts" )
                            
    


                



        print("In watch subcription thread ")
#        print(f"       {task_queue}")
        print(sthread_list)

        print(f"       {subscription_thread_list}")
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
                    task_queue.append(asyncio.create_task(monitor_assistant(assistant_id=assistant, entity_list=entity_list)))
        
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
