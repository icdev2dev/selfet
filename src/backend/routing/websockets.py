import time
from flask_socketio import SocketIO
import eventlet
from butils import send_request_to_agent_with_destination_thread_id


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

