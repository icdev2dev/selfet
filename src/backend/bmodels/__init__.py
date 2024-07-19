import json
from .assistants import AutoExecAssistant, get_registry_thread
from .messages import AutoExecListenMessage
from .messages import AutoExecSubMessage
from .threads.sub import AutoExecSubThread
from .threads.listen import AutoExecListenThread


import yaml



def create_registered_agents_from_yaml(yaml_file):
    with open(yaml_file, "r") as file: 
        yaml_data = yaml.safe_load(file)
        for assistant in yaml_data['assistants']:
            name = assistant['name']
            description = assistant['role']
            instructions = assistant['background']

            create_registered_agent_by_name(name=name, description=description, instructions=instructions)


def delete_all_registered_agents() :

    for agent in AutoExecAssistant.list():
        print(f"Now deleting {agent.id}")
        AutoExecAssistant.delete(agent.id)
    print("Done deleting ALL agents")

def create_registered_agent_by_name(name, instructions, description): 

    instructions = f" " + instructions
    
    AutoExecAssistant.create(name=name, instructions=instructions, description=description)


def delete_registered_agent_by_name(name): 
    idd_assistant = None

    list_registered_assistants = AutoExecAssistant.list()

    for registered_assistant in list_registered_assistants:
        if registered_assistant.name == name:
            idd_assistant = registered_assistant
            break
        
    if idd_assistant:
        AutoExecAssistant.delete(idd_assistant.id)        




def find_communication_channel_for_agent(common_name):

        registry_thread = get_registry_thread()
        if registry_thread: 
            for msg in registry_thread.list_messages():
                agent_data = json.loads(msg.content[0].text.value)
                if agent_data["common_name"] == common_name:
                    return agent_data["communication_channel"]
            else:
                return None           
        else:
            return None

