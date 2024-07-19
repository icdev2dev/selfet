from typing import Optional, List, Dict, Type, TypeVar

import json
from pydantic import Field, BaseModel, model_serializer

from openai_session_handler.models.beta import register_composite_fields_and_type
from openai_session_handler.models.assistants.baseassistant import BaseAssistant
from openai_session_handler.models.threads.basethread import BaseThread


T = TypeVar('T', bound='AutoExecAssistantRegistry')


class AutoExecSystemThreadTracker(BaseAssistant):
    autoexecsystemthreads_1:Optional[str] = Field(default="")
    
    class AutoExecSystemBaseThread(BaseModel):
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

    register_composite_fields_and_type("autoexecsystemthreads", ["autoexecsystemthreads_1"], AutoExecSystemBaseThread)
    
    @property
    def autoexecsystemthreads(self) -> List[AutoExecSystemBaseThread]:
        return self.get_composite_field("autoexecsystemthreads")

    def add_autoexecsystemthread(self, thread_id):
        autoexecsystemthreads = self.autoexecsystemthreads

        autoexecsystembasethread = AutoExecSystemThreadTracker.AutoExecSystemBaseThread(thread_id=thread_id)
        
        autoexecsystemthreads.append(autoexecsystembasethread)

        self.save_composite_field("autoexecsystemthreads", autoexecsystemthreads)




class AutoExecAssistantRegistry(BaseThread):
    @classmethod
    def create(cls:Type[T], **kwargs) -> T:

        if len(AutoExecSystemThreadTracker.list()) == 0:
            autoexecsystemthread_tracker = AutoExecSystemThreadTracker.create()
        else:
            autoexecsystemthread_tracker = AutoExecSystemThreadTracker.list()[0]
        
        if len(autoexecsystemthread_tracker.autoexecsystemthreads) == 0:
            autoexecsystemthread = super().create(**kwargs)
            autoexecsystemthread_tracker.add_autoexecsystemthread(thread_id=autoexecsystemthread.id)
        else:
            autoexecsystemthread = autoexecsystemthread_tracker.autoexecsystemthreads[0]

        return autoexecsystemthread
    
      

    @classmethod
    def delete(cls:Type[T], thread_id) :
        pass 


    @classmethod
    def list(cls:Type[T]) -> List[T]:
        if len(AutoExecSystemThreadTracker.list()) == 0:
            return []
        else:
            return  [AutoExecSystemThreadTracker.list()[0].autoexecsystemthreads[0]]
        


