import yaml
import flask
from flask import jsonify

from routing.providers import get_providers, get_models


def index(): 
    return jsonify("hello")

def configure_routing(app:flask.app.Flask):
    app.add_url_rule("/", view_func=index)

    app.add_url_rule("/providers", view_func=get_providers)
    app.add_url_rule("/models/<provider>", view_func=get_models)


