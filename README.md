# Background

This project is a demonstration of a framework to build out autonomous agents.

Broadly I define autonomous agents as agents that work independently; but co-operatively; 
with other agents to accomplish certain goals. 

We will use the example of using three person to illustrate the concept of autonomous 
agents before diving deeper into code.

# High Level Conceptual Architecture

## Three Persons
Let's assume that we have these three individuals working in a company : 

(a) Aileen -- who is a trend identifier
(b) Sheila -- who is a trend demand forecaster
(c) Mary   -- who is involved in developing recommendation systems

The details of these agents is in src/backend/data/assistants.yaml. 

If these agents are to work in a co-operative fashion, they should know 
about each other's exisistence as well as how to communicate with each other.

## The task
If one of the agents is given a task, say 
"Hi @Mary, can you provide three novel ideas to use for a hackathon?"
then the general concept is for Mary to provide three novel ideas but ask for 
feedback from others on the team for these ideas.

This conversation should be transparent and, more-or-less, free flowing leading
towards some conclusions. 

## End Point

Since left to themselves, these sorts of conversations will be interminable. At some point, 
a hard decision is made to close the conversation.

## Some Key Callouts

### Number of Persons
Obviously the number of the persons should not be fixed. 

### Common Communication Channel/s 
The personas should know where to read from and where to write to. In most cases (but not all), 
the reading and writing is done from the same communication channel (aka subscription thread).

### Personal Communication Channel 
There must be a channel that an agent should know where other agents/system can send a message that 
is exclusive for their use. This is called Personal Communication Channel (aka pcc, listen thread).

### Agent Registry
There must be a place where all known agents can register their pcc so that others can communicate 
to specific agents through their pcc.


# High Level Run Time

## Pre-requisites
### pip install 
src/backend/requirements.txt contains the requirements associated to create a virtual environment
source the environment

### API Keys
Both OPENAI_API_KEY and GROQ_API_KEY are required. 
 
## butils -- PART I SETUP
butils is the common place to initiate things from the command line with the relevant venv
Open ORIGINAL terminal to source your virtual environment and API keys

### Create registered_agents
>>> from butils import create_registered_agents_from_yaml, list_registered_agents
>>> create_registered_agents_from_yaml("data/assistants.yaml")
>>> list_registered_agents()

### Create Common Communication Channel (aka subscription thread)
>>> from butils import create_subscription_thread, list_subscription_threads
>>> create_subscription_thread()

## bserver -- PART II Main Run Time
In ANOTHER terminal, start bserver (which is expected to run forever) with venv and sourced API KEYS
and observe output
python bserver.py

## butils -- PART III Send commands to agents
Go back to the ORGINAL terminal 

>>> from butils import send_request_to_agent

>>> send_request_to_agent("Mary", "Can you please give three novel themes for the hackathon? We can refine the themes further through colloboration; if required")

Observe output in the ANOTHER terminal

>>> send_request_to_agent("Aileen", "What do you think?")

Observe output in the ANOTHER terminal

>>> send_request_to_agent("Sheila", "What do you think?")

Observe output in the ANOTHER terminal




