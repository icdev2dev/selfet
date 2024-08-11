

from typing import Optional, List, Dict, Type, TypeVar

import json
from pydantic import Field, BaseModel, model_serializer

from openai_session_handler.models.beta import register_composite_fields_and_type
from openai_session_handler.models.assistants.baseassistant import BaseAssistant
from openai_session_handler.models.threads.basethread import BaseThread
from ..messages import from_message_to_autoexecsubmessage
from ..messages import AutoExecSubMessage


T = TypeVar('T', bound='AutoExecSubThread')


class AutoExecSubThreadTracker(BaseAssistant):

    autoexecsubthreads_1:Optional[str] = Field(default="")
    autoexecsubthreads_2:Optional[str] = Field(default="")

    class AutoExecSubBaseThread(BaseModel):
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

    register_composite_fields_and_type("autoexecsubthreads", ["autoexecsubthreads_1", "autoexecsubthreads_2"], AutoExecSubBaseThread)

    @property
    def autoexecsubthreads(self) -> List[AutoExecSubBaseThread]:
        return self.get_composite_field("autoexecsubthreads")
    

    def add_autoexecsubthread(self, thread_id):
        autoexecsubthreads = self.autoexecsubthreads

        autoexecsubbasethread = AutoExecSubThreadTracker.AutoExecSubBaseThread(thread_id=thread_id)
        
        autoexecsubthreads.append(autoexecsubbasethread)

        self.save_composite_field("autoexecsubthreads", autoexecsubthreads)

    def delete_autoexecsubthread(self, thread_id):
        
        autoexecsubthreads_updated = []

        for autoexecsubbasethread in self.autoexecsubthreads:
            if autoexecsubbasethread.thread_id == thread_id:
                pass
            else:
                autoexecsubthreads_updated.append(autoexecsubbasethread)
        
        self.save_composite_field("autoexecsubthreads",autoexecsubthreads_updated )


class AutoExecSubThread(BaseThread):
    originator:Optional[str] = Field(default="")
    max_msgs_on_thread:Optional[str] = Field(default="20")


    @classmethod
    def create(cls:Type[T], **kwargs) -> T:

        if len(AutoExecSubThreadTracker.list()) == 0:
            autoexecsubthread_tracker = AutoExecSubThreadTracker.create()
        else:
            autoexecsubthread_tracker = AutoExecSubThreadTracker.list()[0]
        
        autoexecsubthread = super().create(**kwargs)
        autoexecsubthread_tracker.add_autoexecsubthread(thread_id=autoexecsubthread.id)
        
        return autoexecsubthread

    @classmethod
    def delete(cls:Type[T], thread_id):
        if len(AutoExecSubThreadTracker.list()) == 0:
            pass
        else:
            autoexecsubthread_tracker = AutoExecSubThreadTracker.list()[0]

            autoexecsubthread_tracker.delete_autoexecsubthread(thread_id=thread_id)
            return super().delete(thread_id=thread_id)
    

    @classmethod
    def list(cls:Type[T]):
        if len(AutoExecSubThreadTracker.list()) == 0:
            return []
        else:
            return AutoExecSubThreadTracker.list()[0].autoexecsubthreads


    def number_of_messages(self, limit: int = 100, order: str = "desc", after: str = None, before: str = None ) -> int:
        return len(self.list_messages())


    def list_messages(self, limit: int = 100, order: str = "desc", after: str = None, before: str = None) -> List[AutoExecSubMessage]:

        list_sub_messages = []

        while True:
            list_msg_msgs = super().list_messages(limit, order, after, before)
            if len(list_msg_msgs) == 0:
                break
            else:
                for msg in list_msg_msgs:
                    list_sub_messages.append(from_message_to_autoexecsubmessage(msg))

                if len(list_msg_msgs) == limit:
                    after = list_msg_msgs[-1].id
                else:
                    break
       
        return list_sub_messages
    
      
