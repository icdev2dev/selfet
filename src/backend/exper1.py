import eventlet
eventlet.monkey_patch()


import asyncio
import openai

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS


from routing.flask_routing import configure_http, configure_ws

from routing.conversations import watch_conversations
from routing.agents import watch_assistants

RESOURCEWATCHER_SLEEP_TIME = 15

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5173"}})
socketio = SocketIO(app, async_mode='eventlet',  cors_allowed_origins=["http://127.0.0.1:5173"])


configure_http(app=app)
configure_ws(socketio)




async def resource_watcher(task_watcher, task_queue, agents, conversations ):


    while True:
        print(f"now in resource watcher --> {conversations}")

        try:
            await watch_conversations(task_watcher, task_queue, conversations, socketio)
            
            watch_assistants(task_queue, agents, socketio)
            await asyncio.sleep(RESOURCEWATCHER_SLEEP_TIME)

        except asyncio.exceptions.CancelledError as ce:
            print("A task was cancelled")
        except openai.APITimeoutError :
            print("OpenAI Timeerror....waiting for some time before retrying...")
            await asyncio.sleep(10)
            continue    



async def main():
    task_queue = []
    task_watcher = []
    agents = []
    conversations = []

    resource_watcher_task = asyncio.create_task (resource_watcher(task_watcher=task_watcher,task_queue=task_queue, 
                                                                  agents=agents,
                                                                  conversations=conversations
                                                                  ))
    task_watcher.append({
         'type': 'resource_watcher',
         'id': 0,
         'task': resource_watcher_task
     })

    task_queue.append(resource_watcher_task)
    
    await asyncio.gather(*task_queue)
        


def background_task():
    with app.app_context():  # No async needed here
        print("Running background task...")
        asyncio.run(main())


def start_background_tasks():
    eventlet.spawn(background_task)  # Use eventlet's spawn to start the task

def start_app():
    start_background_tasks()  # Start the background task
    socketio.run(app)

if __name__ == "__main__":
    start_app()
