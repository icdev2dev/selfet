
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO

from routing.flask_routing import configure_routing, configure_ws, init_routing

from bserver import main
import asyncio

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5173"}})
socketio = SocketIO(app, cors_allowed_origins=["http://127.0.0.1:5173"])


init_routing(socketio=socketio)
configure_routing(app=app)
configure_ws(socketio)





def start_app():
    socketio.start_background_task(asyncio.run, main())
    socketio.run(app)

if __name__ == "__main__":
    start_app()
