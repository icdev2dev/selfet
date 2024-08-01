import json
from .assistants.autoexecassistant import AutoExecAssistant, get_registry_thread, delete_all_registered_agents
from .assistants.autoexecassistant import create_registered_agents_from_yaml, list_registered_agents_in_registry


from .threads.listen import AutoExecListenThread


def get_agents() : 
    return    [x.name for x in AutoExecAssistant.list()]


def get_agent_details(agent_name) : 

    agent_details = {
    }

    for agent in AutoExecAssistant.list():
        if agent.name == agent_name: 
            agent_details['role'] = agent.description
            agent_details['instructions'] = agent.instructions
            agent_details['communication_channel'] = find_communication_channel_for_agent(common_name=agent_name)

            if agent_details['communication_channel']:
                communication_channel_thread = AutoExecListenThread.retrieve(agent_details['communication_channel'])
#                print(communication_channel_thread)
                num_messages_in_communication_channel = get_number_of_messages_in_communication_channel(communication_channel_thread=communication_channel_thread)
                agent_details['num_messages_in_communication_channel'] = num_messages_in_communication_channel
            break
    
    return agent_details




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



def get_number_of_messages_in_communication_channel(communication_channel_thread:AutoExecListenThread) -> int:

    limit_max_msgs = 3
    after = None

    countMsgs = 0

    while True:
        msgs = communication_channel_thread.list_messages(limit=limit_max_msgs, after=after )
        if msgs:
            if len(msgs) == limit_max_msgs:
                after = msgs[-1].id
                countMsgs = countMsgs + limit_max_msgs
            else: 
                countMsgs = countMsgs + len(msgs)
                break
        else:
            break

    print(countMsgs)


    return countMsgs




