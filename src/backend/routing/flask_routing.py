import flask
from flask import jsonify, request

from routing.providers import get_providers as providers, get_models as models

from routing.agents import get_agents as agents, get_agent_details as agent_details
from routing.conversations import get_active_conversations as active_conversations, get_inactive_conversations as inactive_conversations, delete_all_inactive_conversations

from routing.conversations import get_conversation as conversation, create_conversation, set_conversation_type

import eventlet

from flask_socketio import SocketIO

from butils import list_active_subscription_threads

from routing.websockets import post_request

MAP_WS_FUNCS = {
    'post_request': post_request
}

def index(): 
    return jsonify("hello")


MAP_HTTP_FUNCS = [
    ["/", index],
    ["/providers", providers],
    ["/models/<provider>", models],
    
    ["/agents", agents],
    ["/agent_details/<agent_name>", agent_details],
    

    ["/create_conversation", create_conversation, ['POST']],
    ["/delete_all_inactive_conversations", delete_all_inactive_conversations, ['POST']],
    ["/conversation/<conversationId>", conversation],
    ["/active_conversations", active_conversations],
    ["/inactive_conversations", inactive_conversations],
    ["/set_conversation_type", set_conversation_type, ['POST']]
]




def monitor_subscription_threads(socketio):
    def wrapper():
        while True:
            print("Now monitoring subscription threads")

            subscription_threads = list_active_subscription_threads()

            hasNewMessageBeenAdded = False

            for subscription_thread in subscription_threads:
                msgs_on_sub_thread = subscription_thread.list_messages()
    
                print(f"{subscription_thread.id} -> {subscription_thread.max_msgs_on_thread} : {len(msgs_on_sub_thread)}")

                if len(msgs_on_sub_thread) != 0:
                    if subscription_thread.hwm != msgs_on_sub_thread[0].id :
                        subscription_thread.set_hwm(msgs_on_sub_thread[0].id)
                        hasNewMessageBeenAdded = True

                if len(msgs_on_sub_thread) > int(subscription_thread.max_msgs_on_thread):
                    print(f"Now making thread {subscription_thread.id} INACTIVE") 
                    subscription_thread.make_subthread_inactive()

                    socketio.emit("madeConversationInactive", {'thread_id': subscription_thread.id })
        
            if hasNewMessageBeenAdded : 
                socketio.emit("newMessageAdded", {                    
                })

            eventlet.sleep(10)
    return wrapper


def init_routing(socketio):
    eventlet.spawn(monitor_subscription_threads(socketio=socketio))


def handle_request_response(data, socketio:SocketIO):
    sid = request.sid
    real_request = data['realRequest']

    MAP_WS_FUNCS[real_request](data=data, socketio=socketio, sid=sid)()




def configure_ws(socketio:SocketIO) :
    def wrapper(data):
        handler = handle_request_response(data, socketio)
    socketio.on('request_response')(handler=wrapper)



def configure_http(app:flask.app.Flask):
    for http_func in MAP_HTTP_FUNCS:
        if len(http_func) == 2:
            app.add_url_rule(http_func[0], view_func=http_func[1])
        elif len(http_func) == 3:
            app.add_url_rule(http_func[0], view_func=http_func[1],methods=http_func[2])
        else: 
            print(f"Unknown config in MAP_HTTP_FUNCS : {http_func}")






    


        
