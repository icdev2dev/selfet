import openai
import asyncio
import json

from .autoexecassistant import AutoExecAssistant, list_registered_agents_in_registry as list_registered_agents
from bmodels.threads.listen import AutoExecListenThread
from bmodels.threads.sub import AutoExecSubThread
from bmodels.exceptions import APIException
from bmodels.messages import AutoExecSubMessage


from tools_utils import groq_chat



GENERAL_COMMUNICATION_STYLE = """
Please introduce yourself at the start of every messaage; so that others know who you are as well as
be able to respond back to you. Please prefix with '@'. You may give a relevant background if you feel like it. 
Even in your description, please prefix with '@' on your name. 

Also others will also use the same format 
to identify themselves. Therefore you can respond to messages in a personalized way; if the 
situation calls for it. Obviously when you refer to others in the team, you should also prefix 
their names with a '@'. 

You SHOULD obviously **REFRAIN** from subsequently addressing yourself in the message.
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

    The term feedback is expected to be used in context. For example, if your role is teacher and others are student,
    obviously the term feedback is expected to be worded differently.

    Additionally the conversation must lead to some closure; though opinions of others are definitely required 
    and welcome. However even if the team may have divergent opinions, it is better to agree to disagree rather 
    than have incessant conversations. 

    In some contexts and situations, the conversation will naturally gravitate towards closure of sorts. Encourage that.
    """
    return TEAM_COMPOSITION







class AsyncAssistant: 
   
    def __init__(self, assistant_id, entity_list):
        self.assistant_id = assistant_id
        self.entity_list = entity_list

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
            await asyncio.sleep(10)

    def process_listen_msgs(self,assistant, thread_msgs,chat_model = groq_chat, model="llama-3.1-8b-instant") :

        name = assistant.name

        print(name)
        print(chat_model)

        for thread_msg in thread_msgs:

            class_type = thread_msg.class_type
            print(class_type)

            destination_thread_id = thread_msg.destination_thread_id
            as_thread = AutoExecSubThread.retrieve(thread_id=destination_thread_id)

            previous_messages = []

            for message in as_thread.list_messages():
                previous_messages.append({'role': message.role, 'content': message.content[0]['text'].value})

            prompt = thread_msg.content[0]['text'].value

            messages=[]
            
            messages.append ({'role': 'system',
                            "content": f"YOU are {name}. PLEASE USE **{name}** when you introduce yourself. In every message please mention your name which is **{name}** \n" 
                            })        
            messages.append ({'role': 'system',
                            "content": assistant.instructions 
                            })
            messages.append ({'role': 'system',
                            "content": f"YOU are {name}. Always start with @{name} here. {GENERAL_COMMUNICATION_STYLE}" 
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


            AutoExecSubMessage.create(thread_id=destination_thread_id, content=second_response.choices[0].message.content, originator=name)




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
            
