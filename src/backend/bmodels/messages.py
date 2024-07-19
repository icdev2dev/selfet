
from typing import Dict, List, Optional, Type, TypeVar
from openai.types.beta.threads.message import Message
from openai_session_handler.models.messages.basemessage import BaseMessage
import json
from pydantic import Field, BaseModel, model_serializer


class AutoExecPostMessage (BaseMessage):
    """
    This is the message that goes into the AutoExecPostThread
    """
    real_role:Optional[str] = Field(default="")    # the meaning of this role is in processing context
                                                   # i.e. system, summary etc


class AutoExecSubMessage(BaseMessage):
    originator:Optional[str] = Field(default="")
    


class AutoExecListenMessage (BaseMessage):
    """
    This is the message that goes into the listen_thread of the assistant
    Either as a request or a response
    """

    uuid: Optional[str] = Field(default="")
    r_uuid: Optional[str] = Field(default="")

    
    class_type: Optional[str] = Field(default="")          # Request | Response
    class_type_subtype: Optional[str] = Field(default="")  # "New" | "Feedback" | "Acknowledgement"  etc 
    
    destination_thread_id:Optional[str] = Field(default="")
    source_thread_id:Optional[str] = Field(default="")
    source_thread_read_type: Optional[str] = Field(default="")   # "All" | "Last" | "SinceLastSummary" | "SinceLastToLastSummary"


def from_message_to_autoexecsubmessage(msg:Message) -> AutoExecSubMessage:

    content = msg.content[0]
    ae = AutoExecSubMessage(thread_id=msg.thread_id, role=msg.role, content=[{'text': content.text, 'type': content.type}])

    exclude_fields = set(['thread_id', 'role', 'content', 'attachments'])
    message_fields = set(list(msg.__annotations__.keys()))
    copy_message_fields = message_fields - exclude_fields
    
    all_fields = set( list(AutoExecSubMessage.get_all_annotations().keys()))

    for field in copy_message_fields:
        setattr(ae, field, getattr(msg, field))

    for field in all_fields - message_fields:
        setattr(ae, field, msg.metadata[field])
        
    return ae


def from_message_to_autoexeclistenmessage(msg:Message) -> AutoExecListenMessage:

    content = msg.content[0]
    ae = AutoExecListenMessage(thread_id=msg.thread_id, role=msg.role, content=[{'text': content.text, 'type': content.type}])

    exclude_fields = set(['thread_id', 'role', 'content', 'attachments'])
    message_fields = set(list(msg.__annotations__.keys()))
    copy_message_fields = message_fields - exclude_fields
    
    all_fields = set( list(AutoExecListenMessage.get_all_annotations().keys()))

    for field in copy_message_fields:
        setattr(ae, field, getattr(msg, field))

    for field in all_fields - message_fields:
        setattr(ae, field, msg.metadata[field])
        
    return ae

