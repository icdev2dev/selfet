from openai_session_handler.models.assistants.baseassistant import BaseAssistant
from pydantic._internal._model_construction import ModelMetaclass
from pydantic import Field, model_serializer, BaseModel, create_model
from typing import Optional, Dict, List, Type

import json
from openai_session_handler.models.beta import register_composite_fields_and_type


class ThreadTrackerMaker(ModelMetaclass):
    def __new__(cls, name, bases, dct, thread_name, number_of_metadata_vars=4):

        for i in range(number_of_metadata_vars):
            field_name = f"{thread_name.lower()}_{i+1}"
            dct[field_name] = Field(default="")
            if '__annotations__' not in dct:
                dct['__annotations__'] = {}
            dct['__annotations__'][field_name] = Optional[str]

        inner_class_name = f"{thread_name}BaseClass"
        inner_class = create_model(inner_class_name, thread_id = (str, Field(...)), __base__=BaseModel)

        def compact_ser(self) -> str:
            return self.thread_id
        
#            return json.dumps([self.thread_id])

        def compact_deser(string: str) -> Dict :
            return {'thread_id': string}
            list_fields = json.loads(string)
            return {
                    'thread_id': list_fields[0]
            }
        
        setattr(inner_class, "compact_ser", model_serializer(compact_ser) )
        setattr(inner_class, "compact_deser", staticmethod(compact_deser))

        dct[inner_class_name] = inner_class
        dct['__annotations__'][inner_class_name] = Type[inner_class]
                
        register_composite_fields_and_type(f"{thread_name.lower()}s", [f"{thread_name.lower()}_{i+1}" for i in range(number_of_metadata_vars) ], dct[inner_class_name])

        property_name = f"{thread_name.lower()}s"
        def dynamic_property(self) -> List[dct[inner_class_name]]:
            return self.get_composite_field(f"{thread_name.lower()}s")
        dct[property_name] = property(dynamic_property)

        def __json__(self):
            return dict(self)

        dct['__json__'] = __json__
        

        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct, thread_name):
        super().__init__(name, bases, dct)


class AutoExecSubThreadTracker(BaseAssistant, metaclass=ThreadTrackerMaker, thread_name="AutoExecSubThread"):
    pass 


if __name__ == "__main__":

    print(AutoExecSubThreadTracker.list())
    a = AutoExecSubThreadTracker()

    print(a.autoexecsubthreads)

#print(AutoExecSubThreadTracker.list())
