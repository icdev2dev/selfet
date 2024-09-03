import time
from flask_socketio import SocketIO
import eventlet
from butils import send_request_to_agent_with_destination_thread_id
from butils import AutoExecSubMessage



def delete_message(data, socketio:SocketIO, sid):

    def wrapper():
        retVal = AutoExecSubMessage.delete(thread_id=data['thread_id'], message_id=data['message_id'])
        print(str(retVal))
        
    return wrapper

def update_story_state(data, socketio:SocketIO, sid):
    def wrapper():


        print("REDALLLLL")
        print(f"{data['thread_id']}, {data['message_id']}, {data['message_story_state']}")

        aest = AutoExecSubMessage.retrieve(thread_id=data['thread_id'], message_id=data['message_id'])
        aest.update_story_state(data['message_story_state'])

    return wrapper



def update_post_request(data, socketio:SocketIO, sid):
    def wrapper (): 
        
        respond_at = data['respondAt']

        socketio.emit(respond_at, {'status':'success'})

    return wrapper
    




def post_request(data,  socketio:SocketIO, sid):
    def wrapper():
        print(f"{data['realRequestData']}, {data['originator']}, {data['destination_thread_id']}")

        common_name = data['originator']
        real_request_data = data['realRequestData']
        destination_thread_id = data['destination_thread_id']

        

        send_request_to_agent_with_destination_thread_id(common_name=common_name, 
                                                         request=real_request_data,
                                                        destination_thread_id=destination_thread_id )
        
        eventlet.spawn_after(1, update_post_request(data=data, socketio=socketio, sid=sid))
    return wrapper

