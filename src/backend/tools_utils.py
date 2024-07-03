from typing import List, Dict

FUNCTIONS_TYPE_MAP = {
    'str': "string",
    'int': "integer",
    'List': 'array'
}

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
                    function['parameters']['properties'][input_arg_name]['items'] = {}
                    ip_item_type = raw_annotation.__origin__.__args__[0].__name__
                    if ip_item_type in FUNCTIONS_TYPE_MAP:
                        function['parameters']['properties'][input_arg_name]['items']['type'] = FUNCTIONS_TYPE_MAP[ip_item_type]
                    else:
                        function['parameters']['properties'][input_arg_name]['items']['type'] = ip_item_type

            else:
                ip_type =  raw_annotation.__origin__.__name__
                function['parameters']['properties'][input_arg_name]['type'] = ip_type


            function['parameters']['properties'][input_arg_name]['type'] = ip_type
            function['parameters']['properties'][input_arg_name]['description'] = raw_annotation.__metadata__[0]

        tools_functions[func.__name__] = function


        return func
    return wrapper
