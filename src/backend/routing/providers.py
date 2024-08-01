import yaml

from flask import jsonify

with open("data/providers.yaml", "r") as file:
    PROVIDERS = yaml.safe_load(file)

def get_providers(): 
    return jsonify([key for key in PROVIDERS.keys()])


def get_models(provider):
    if provider in PROVIDERS.keys(): 
        return jsonify(PROVIDERS[provider])
    else:
        return jsonify([])
    
    