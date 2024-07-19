from typing import Optional, List, Type, TypeVar
import json
from pydantic import Field, BaseModel, model_serializer
from .threads.listen import AutoExecListenThread
from .threads.system import AutoExecAssistantRegistry

import openai
from openai_session_handler.models.threads.basethread import BaseThread
from openai_session_handler.models.assistants.baseassistant import BaseAssistant

from openai_session_handler.models.beta import register_composite_fields_and_type

T = TypeVar('T', bound='AutoExecAssistantRegistry')


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
        
        

def add_registered_agent_in_registry(id, common_name, communication_channel):
        registry_thread = get_registry_thread()
        if registry_thread: 
    
            data = json.dumps({"entity_type": "assistant", 
                       "id": id, 
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

        add_registered_agent_in_registry(id=assistant.id, common_name=assistant.name, communication_channel=listen_thread.id)
        return assistant
    

    @classmethod
    def delete(cls:Type[T], assistant_id):
        _a = cls.retrieve(assistant_id=assistant_id)

        AutoExecListenThread.delete(thread_id=_a.listen_thread)

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








    

