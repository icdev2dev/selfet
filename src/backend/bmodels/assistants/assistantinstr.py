import json
import copy

from .autoexecassistant import AutoExecAssistant, list_registered_agents_in_registry as list_registered_agents


GENERAL_COMMUNICATION_STYLE = """
Please introduce yourself at the start of every messaage; so that others know who you are as well as
be able to respond back to you. Please prefix with '@'. You may give a relevant background if you feel like it. 
Even in your description, please prefix with '@' on your name. 

Also others will also use the same format 
to identify themselves. Therefore you can respond to messages in a personalized way; if the 
situation calls for it. Obviously when you refer to others in the team, you should also prefix 
their names with a '@'. 

You SHOULD obviously **REFRAIN** from subsequently addressing yourself in the message.
"""


def team_composition(): 
    TEAM_COMPOSITION = """Your team consists of the following team members (including you) 
    along with their backgrounds.\n"""


    for r_a in list_registered_agents():
        r_a = json.loads(r_a)
        TEAM_COMPOSITION = TEAM_COMPOSITION + f"\n {r_a['common_name']} : "
        assistant = AutoExecAssistant.retrieve(assistant_id=r_a['id'])

        TEAM_COMPOSITION = TEAM_COMPOSITION + assistant.instructions

    TEAM_COMPOSITION = TEAM_COMPOSITION + """You may ask for feedback from others on the team; if relevant. 
    You don't have to. However whenever someone asks you to ask your team members, you MUST ONLY use the 
    team mates mentioned above. Once again you are not obliged to call on your team members if you don't feel
    like it.

    The term feedback is expected to be used in context. For example, if your role is teacher and others are student,
    obviously the term feedback is expected to be worded differently.

    Additionally the conversation must lead to some closure; though opinions of others are definitely required 
    and welcome. However even if the team may have divergent opinions, it is better to agree to disagree rather 
    than have incessant conversations. 

    In some contexts and situations, the conversation will naturally gravitate towards closure of sorts. Encourage that.
    """
    return TEAM_COMPOSITION

def system_instructions(name, instructions):
    messages = []
            
    messages.append ({'role': 'system',
                    "content": f"YOU are {name}. PLEASE USE **{name}** when you introduce yourself. In every message please mention your name which is **{name}** \n" 
                    })        
    messages.append ({'role': 'system',
                    "content": instructions 
                    })
    messages.append ({'role': 'system',
                    "content": f"YOU are {name}. Always start with @{name} here. {GENERAL_COMMUNICATION_STYLE}" 
                    })
    messages.append ({'role': 'system',
                    "content": team_composition() 
                    })

    return copy.deepcopy(messages)



