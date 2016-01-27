import os
import json

from vwpy.modelschema import load_schemas

from flask import Blueprint, render_template, jsonify

blueprint = Blueprint("api", __name__, url_prefix='/api',
                      static_folder="../static")


@blueprint.route("/")
def api():
    data = {'title': 'vwmodels',
            'version': 1.0,
            'description': 'The model Server api endpoint for virtual watershed platform.',
            'models': load_schemas()
            }
    return jsonify(data)


@blueprint.route("/schema/<model>")
def modelschema(model):
    data = load_schemas(model)
    return jsonify(data)
