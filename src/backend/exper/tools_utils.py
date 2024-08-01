from typing import List, Dict
from groq import Groq
from openai import OpenAI


FUNCTIONS_TYPE_MAP = {
    'str': "string",
    'int': "integer",
    'List': 'array'
}


class ChatAPIWrapper:
    def __init__(self, client):
        self.chat = self.Chat(client.chat)

    class Chat:
        def __init__(self, chat):
            self.completions = chat.completions


groq_chat = ChatAPIWrapper(client=Groq())
openai_chat = ChatAPIWrapper(client=OpenAI())



def add_enum_to_param(tools, function_name, param, enum):
    for tool in tools:
        if tool['type'] == 'function' and tool['function']['name'] == function_name:
            if param in  tool['function']['parameters']['properties'].keys():
                tool['function']['parameters']['properties'][param]['enum'] = enum
                
            else:
                print(f"{param} not in function {function_name}")
                break
            
            break
    return tools


def include_one_tools_function(tools_functions, ret_val=[])-> List[Dict] :

    import copy
    tools_functions = copy.deepcopy(tools_functions)
    for tool_function_name in tools_functions.keys():
        if tool_function_name == "call_objective":
            ret_val.append( {
                "type": "function", 
                "function": tools_functions[tool_function_name]
            })

    return ret_val


def include_all_tools_functions(tools_functions, ret_val=[])-> List[Dict] :

    import copy
    tools_functions = copy.deepcopy(tools_functions)
    for tool_function_name in tools_functions.keys():
        
        ret_val.append( {
            "type": "function", 
            "function": tools_functions[tool_function_name]
        })

    
    for val in ret_val:
        del val['function']['function']
            


    return ret_val

def tools_function(tools_functions): 
    def wrapper(func):

        function = dict()
        function['function'] = func
        function['name'] = func.__name__
        function['description'] = func.__doc__
        function['parameters'] = {}
        function['parameters']['type'] = "object"
        function['parameters']['properties'] = {}

        

        input_arg_names = [arg_name for arg_name in func.__code__.co_varnames[:func.__code__.co_argcount]]

        for input_arg_name in input_arg_names:
            function['parameters']['properties'][input_arg_name] = {}
            raw_annotation = func.__annotations__[input_arg_name]


            if raw_annotation.__origin__.__name__ in FUNCTIONS_TYPE_MAP:
                ip_type = FUNCTIONS_TYPE_MAP[raw_annotation.__origin__.__name__]
                function['parameters']['properties'][input_arg_name]['type'] = ip_type

                if ip_type == 'array':
                    
                    print('in array')
                    function['parameters']['properties'][input_arg_name]['items'] = {}
                    function['parameters']['properties'][input_arg_name]['items']['type'] = 'str'

 #                   ip_item_type = raw_annotation.__origin__.__name__
 #                   if ip_item_type in FUNCTIONS_TYPE_MAP:
 #                       function['parameters']['properties'][input_arg_name]['items']['type'] = FUNCTIONS_TYPE_MAP[ip_item_type]
 #                   else:
 #                       function['parameters']['properties'][input_arg_name]['items']['type'] = ip_item_type

            else:
                ip_type =  raw_annotation.__origin__.__name__
                function['parameters']['properties'][input_arg_name]['type'] = ip_type


            function['parameters']['properties'][input_arg_name]['type'] = ip_type
            function['parameters']['properties'][input_arg_name]['description'] = raw_annotation.__metadata__[0]

        tools_functions[func.__name__] = function


        return func
    return wrapper
