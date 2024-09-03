import openai
import asyncio
import json

from .autoexecassistant import AutoExecAssistant, list_registered_agents_in_registry as list_registered_agents
from bmodels.threads.listen import AutoExecListenThread
from bmodels.threads.sub import AutoExecSubThread
from bmodels.exceptions import APIException
from bmodels.messages import AutoExecSubMessage

from tools_utils import groq_chat, openai_chat

from .assistantinstr import system_instructions



class AsyncAssistant: 
   
    def __init__(self, assistant_id, entity_list, assistant_watch_sleep_time, socketio):
        self.assistant_id = assistant_id
        self.entity_list = entity_list
        self.assistant_watch_sleep_time = assistant_watch_sleep_time
        self.socketio = socketio


        self.autoexecassistant = AutoExecAssistant.retrieve(assistant_id=self.assistant_id)
        self.listen_thread = AutoExecListenThread.retrieve(thread_id=self.autoexecassistant.listen_thread)
        
    async def __call__(self) :
        while True:
#            print (f"from moni {self.assistant_id} ->  {self.entity_list}")
            if self.assistant_id not in self.entity_list:
                break
            else : 
                try : 
                    self.process_listen_thread ()
                except openai.NotFoundError as e:
                    print(f"{e}")
                    break
                except ( openai.APITimeoutError , openai.APIConnectionError) as e:
                    print("API Error in call")
                    raise APIException from e        
            await asyncio.sleep(self.assistant_watch_sleep_time)

#    def process_listen_msgs(self,assistant, thread_msgs,chat_model = groq_chat, model="llama-3.1-70b-versatile") :
    def process_listen_msgs(self,assistant, thread_msgs,chat_model = openai_chat, model="gpt-4o-mini") :

        name = assistant.name
        instructions = assistant.instructions

 #       print(name)

        for thread_msg in thread_msgs:

            class_type = thread_msg.class_type
            print(class_type)

            destination_thread_id = thread_msg.destination_thread_id
            print(destination_thread_id)
            
            as_thread = AutoExecSubThread.retrieve(thread_id=destination_thread_id)

            previous_messages = []

            for message in as_thread.list_messages():
                # specialized for story
                if message.story_state == 'Draft' or message.story_state == 'Final':
                # end specialized for story

                    previous_messages.append({'role': message.role, 'content': message.content[0]['text'].value})

            prompt = thread_msg.content[0]['text'].value

            messages=[]
            
            for instruction in system_instructions(name, instructions):
                messages.append(instruction)
            
            for message in previous_messages:
                messages.append(message)


            messages.append({'role': 'user', 
                            'content': prompt   
                            })


            second_response = chat_model.chat.completions.create(
                    model=model, messages=messages
                )

            print("\n\nSecond LLM Call Response:", second_response.choices[0].message.content)


            AutoExecSubMessage.create(thread_id=destination_thread_id, content=second_response.choices[0].message.content, originator=name)
            self.socketio.emit("newMessageAdded", {})
            



    def process_listen_thread (self):
            assistant = self.autoexecassistant
            thread = self.listen_thread
            process_in_seq = self.process_listen_msgs

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
                print("API Error in process listen thread")
                raise APIException from e
            
