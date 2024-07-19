import yaml

from flask import Flask, request,jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from flask_routing import configure_routing

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

configure_routing(app=app)

def start_app():
    socketio.run(app)

if __name__ == "__main__":
    start_app()
