import flask
from flask import jsonify

from routing.providers import get_providers, get_models
from routing.agents import get_agents, get_agent_details

def index(): 
    return jsonify("hello")

def configure_routing(app:flask.app.Flask):
    app.add_url_rule("/", view_func=index)

    app.add_url_rule("/providers", view_func=get_providers)
    app.add_url_rule("/models/<provider>", view_func=get_models)

    app.add_url_rule("/agents", view_func=get_agents)
    app.add_url_rule("/agent_details/<agent_name>", view_func=get_agent_details)
    

        
