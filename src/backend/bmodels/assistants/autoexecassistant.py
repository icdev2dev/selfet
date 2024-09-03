from typing import Optional, Type, TypeVar
from pydantic import Field
import json
import yaml

from openai_session_handler.models.assistants.baseassistant import BaseAssistant
from openai_session_handler.models.threads.basethread import BaseThread

from ..threads.listen import AutoExecListenThread
from ..threads.system import AutoExecAssistantRegistry


import openai

T = TypeVar('T', bound="AutoExecAssistantRegistry")



def get_registry_thread() -> BaseThread:

    registry = AutoExecAssistantRegistry.list()

    if len(registry) > 0:
        registry = registry[0]
        registry_thread_id = registry.thread_id
        registry_thread = BaseThread.retrieve(thread_id=registry_thread_id)
        return registry_thread
    else:
        return None


def list_registered_agents_in_registry():

        registry_thread = get_registry_thread()
        if registry_thread: 
            return [msg.content[0].text.value for msg in registry_thread.list_messages()]

def get_registered_agent_by_name(name:str) -> str:

    registry_thread = get_registry_thread()

    if registry_thread: 
            for msg in registry_thread.list_messages():
                value = msg.content[0].text.value
                jvalue = json.loads(value)
                if jvalue['common_name'] == name:
                    return jvalue['id']

    return None


def list_human_agents_in_registry():
        registry_thread = get_registry_thread()
        human_agents = []

        if registry_thread: 
             for msg in registry_thread.list_messages():
                  value = msg.content[0].text.value
                  jvalue = json.loads(value)
                  if jvalue['real_role'] == 'human':
                       human_agents.append(value)
            
        
        return human_agents

        

def add_registered_agent_in_registry(id, real_role, common_name, communication_channel):
        registry_thread = get_registry_thread()
        if registry_thread: 
    
            data = json.dumps({"entity_type": "assistant", 
                       "id": id, 
                       "real_role": real_role,
                       "common_name": common_name,
                       "communication_channel": communication_channel
                       })
            registry_thread.create_message(content=data)
    


def delete_registered_agent_from_registry(id):
        registry_thread = get_registry_thread()
        if registry_thread: 
            for msg in registry_thread.list_messages():
                value, message_id = json.loads(msg.content[0].text.value), msg.id

                if value['id'] == id:
                    registry_thread.delete_message(message_id=message_id)
                    break



def create_registered_agent_by_name(name, instructions, description, real_provider, real_model, real_role): 

    instructions = f" " + instructions
    

    kwargs = {
         'name': name,
         'instructions': instructions,
         'description' : description
    }

    if real_provider:
         kwargs['real_provider'] = real_provider
    if real_model:
         kwargs['real_model'] = real_model
    if real_role:
         kwargs['real_role'] = real_role

    AutoExecAssistant.create(**kwargs)


def delete_registered_agent_by_name(name): 
    idd_assistant = None

    list_registered_assistants = AutoExecAssistant.list()

    for registered_assistant in list_registered_assistants:
        if registered_assistant.name == name:
            idd_assistant = registered_assistant
            break
        
    if idd_assistant:
        AutoExecAssistant.delete(idd_assistant.id)        


def create_registered_agents_from_yaml(yaml_file):
    with open(yaml_file, "r") as file: 
        yaml_data = yaml.safe_load(file)
        for assistant in yaml_data['assistants']:

            real_provider = None
            if 'real_provider' in assistant.keys():
                 real_provider = assistant['real_provider']

            real_model = None
            if 'real_model' in assistant.keys():
                 real_model = assistant['real_model']

            real_role = None
            if 'real_role' in assistant.keys():
                 real_role = assistant['real_role']

            name = assistant['name']
            description = assistant['role']
            instructions = assistant['background']


            create_registered_agent_by_name(name=name, 
                                            description=description, 
                                            instructions=instructions, 
                                            real_provider=real_provider,
                                            real_model=real_model,
                                            real_role=real_role )
            


def delete_all_registered_agents() :

    for agent in AutoExecAssistant.list():
        print(f"Now deleting {agent.id}")
        AutoExecAssistant.delete(agent.id)
    print("Done deleting ALL agents")




class AutoExecAssistant(BaseAssistant):
    real_provider:Optional[str] = Field(default="openai")
    real_model: Optional[str] = Field(default="gpt-4")

    real_role: Optional[str] = Field(default="")

    listen_thread:Optional[str] = Field(default="")


    sub_thread_1:Optional[str] = Field(default="")
    sub_thread_1_hwm:Optional[str] = Field(default="")
    
    sub_thread_2:Optional[str] = Field(default="")
    sub_thread_2_hwm:Optional[str] = Field(default="")


    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        kwargs['assistant_type'] = cls.__name__

        listen_thread = AutoExecListenThread.create()
        kwargs['listen_thread'] = listen_thread.id
        
        cls._reference_class_abc = openai.types.beta.assistant.Assistant 
        assistant =   super().create(**kwargs)

        add_registered_agent_in_registry(id=assistant.id, real_role=assistant.real_role, common_name=assistant.name, communication_channel=listen_thread.id)
        return assistant
    

    @classmethod
    def delete(cls:Type[T], assistant_id):
        _a = cls.retrieve(assistant_id=assistant_id)

        try :
            AutoExecListenThread.delete(thread_id=_a.listen_thread)
        except openai.NotFoundError as nfe: 
             print(str(nfe))

        delete_registered_agent_from_registry(id=assistant_id)

        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return super().delete(assistant_id=assistant_id)

    def subscribe(self, thread_id):

        if (self.sub_thread_1 != "" and self.sub_thread_2 != "") : 
            raise   ValueError("All subscription slots are taken up") 
        elif (self.sub_thread_1 == ""): 
                self.update(sub_thread_1 = thread_id)
        else:  
            self.update(sub_thread_2 = thread_id)

    
    def unsubscribe(self, thread_id):
        if (self.sub_thread_1 == thread_id): 
            self.update(sub_thread_1 = "", sub_thread_1_hwm = "")

        elif (self.sub_thread_2 == thread_id):
            self.update(sub_thread_2 = "", sub_thread_2_hwm = "")


