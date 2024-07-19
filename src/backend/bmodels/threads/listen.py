from typing import Optional, List, Dict, Type, TypeVar

import json
from pydantic import Field, BaseModel, model_serializer

from openai_session_handler.models.beta import register_composite_fields_and_type
from openai_session_handler.models.assistants.baseassistant import BaseAssistant
from openai_session_handler.models.threads.basethread import BaseThread
from openai_session_handler.models.messages.basemessage import BaseMessage

from ..messages import from_message_to_autoexeclistenmessage


T = TypeVar('T', bound='AutoExecListenThread')





class AutoExecListenThread(BaseThread):
    hwm:Optional[str] = Field(default="")

    def list_messages(self, limit: int = 20, order: str = "desc", after: str = None, before: str = None) -> List:
        return    [from_message_to_autoexeclistenmessage(x)  for x in  super().list_messages(limit, order, after, before)]

    def set_hwm (self, hwm: str) :
        self.hwm = hwm
        self.generic_update_metadata()

    def _reset_hwm(self):
        """ only for experimentation"""
        self.hwm = ""
        
        self.generic_update_metadata()


