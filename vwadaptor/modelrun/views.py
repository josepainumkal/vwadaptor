import flask
from flask import Blueprint, render_template
from flask_login import login_required
from flask import jsonify

from .models import ModelRun
import json

blueprint = Blueprint("modelrun", __name__, url_prefix='/api/modelruns',
                      static_folder="../static")


@blueprint.route("/<int:id>/progress")
#@login_required
def progress(id):
    modelrun = ModelRun.query.get(id)
    if modelrun:
      progress = {"modelrun_id":id,"state":modelrun.progress_state,"value":modelrun.progress_value}
      # resp = flask.Response(json.dumps(progress))
      # resp.status_code = 200
      # resp.headers['Content-Type'] = 'application/json'
      return jsonify(progress)
    else:
      err = {"error":"ModelRun {0} Not Found".format(id)}
      return jsonify(err), 404