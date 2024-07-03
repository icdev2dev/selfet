from typing import Dict, List, Optional, Type, TypeVar

import json
from pydantic import Field, BaseModel, model_serializer

from openai_session_handler.models.beta import register_composite_fields_and_type
from openai_session_handler.models.threads.basethread import BaseThread
from openai_session_handler.models.assistants.baseassistant import BaseAssistant

from openai_session_handler.models.messages.basemessage import BaseMessage


T = TypeVar('T', bound='AutoExecThread')

class AutoExecAssistant(BaseAssistant):
    real_provider:Optional[str] = Field(default="openai")
    real_model: Optional[str] = Field(default="gpt-4")

    real_role: Optional[str] = Field(default="")

    listen_thread:Optional[str] = Field(default="")
    listen_thread_hwm:Optional[str] = Field(default="")


    sub_thread_1:Optional[str] = Field(default="")
    sub_thread_1_hwm:Optional[str] = Field(default="")
    
    sub_thread_2:Optional[str] = Field(default="")
    sub_thread_2_hwm:Optional[str] = Field(default="")


    def subscribe(self, thread_id):

        if (self.sub_thread_1 is not "" and self.sub_thread_2 is not "") : 
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


    

class AutoExecThread(BaseThread):
    exec_type:Optional[str] = Field(default="chat", description="options are : assistant|chat")
    bmodel_provider:Optional[str] = Field(default="openai", description="options are openai|Groq")
    actual_model:Optional[str] = Field(default="gpt-4-turbo")

    assistant_id: Optional[str] = Field(default="")
    primary_input_thread_id: Optional[str] = Field(default="")
    

    class PrimaryInputThread(BaseThread):
        hwm:Optional[str] = Field(default="")


    class InputMessage(BaseMessage):
        message_class:Optional[str] = Field(default="P")   # P for primary

    def create_message(self, content) :
        self.InputMessage.create(thread_id=self.primary_input_thread_id, role="user", content=content)

    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        if len(AutoExecThreadTracker.list()) == 0:
            autoexecthread_tracker = AutoExecThreadTracker.create()
        else:
            autoexecthread_tracker = AutoExecThreadTracker.list()[0]
        
        primary_input_thread = cls.PrimaryInputThread.create()

        kwargs['primary_input_thread_id'] = primary_input_thread.id

        autoexecthread = super().create(**kwargs)

        autoexecthread_tracker.add_autoexecthread(thread_id=autoexecthread.id)


    @classmethod
    def delete(cls:Type[T], thread_id):
        if len(AutoExecThreadTracker.list()) == 0:
            pass
        else:
            autoexecthread_tracker = AutoExecThreadTracker.list()[0]

            autoexecthread = cls.retrieve(thread_id=thread_id)
            cls.PrimaryInputThread.delete(thread_id=autoexecthread.primary_input_thread_id)


            autoexecthread_tracker.delete_autoexecthread(thread_id=thread_id)
            return super().delete(thread_id=thread_id)
        

    @classmethod
    def list(cls:Type[T]):
        if len(AutoExecThreadTracker.list()) == 0:
            return []
        else:
            return AutoExecThreadTracker.list()[0].autoexecthreads
        

    @classmethod
    def retrieve(cls: type[T], thread_id) -> T:
        return super().retrieve(thread_id)
    

class AutoExecThreadTracker(BaseAssistant):

    autoexecthreads_1:Optional[str] = Field(default="")
    autoexecthreads_2:Optional[str] = Field(default="")

    class AutoExecBaseThread(BaseModel):
        thread_id:str = Field(...)

        @model_serializer
        def compact_ser(self) -> str:
            return json.dumps([self.thread_id])
        
        @staticmethod
        def compact_deser(string: str) -> Dict :
            list_fields = json.loads(string)
            return {
                'thread_id': list_fields[0]
            }

    register_composite_fields_and_type("autoexecthreads", ["autoexecthreads_1", "autoexecthreads_2"], AutoExecBaseThread)

    @property
    def autoexecthreads(self) -> List[AutoExecBaseThread]:
        return self.get_composite_field("autoexecthreads")
    

    def add_autoexecthread(self, thread_id):
        autoexecthreads = self.autoexecthreads

        autoexecbasethread = AutoExecThreadTracker.AutoExecBaseThread(thread_id=thread_id)
        
        autoexecthreads.append(autoexecbasethread)

        print(autoexecthreads)


        self.save_composite_field("autoexecthreads", autoexecthreads)

    def delete_autoexecthread(self, thread_id):
        
        autoexecthreads_updated = []

        for autoexecbasethread in self.autoexecthreads:
            if autoexecbasethread.thread_id == thread_id:
                pass
            else:
                autoexecthreads_updated.append(autoexecbasethread)
        
        self.save_composite_field("autoexecthreads",autoexecthreads_updated )
        