from flask import Blueprint, render_template,jsonify
from flask_login import login_required

from vwadaptor.constants import PROGRESS_STATES
from vwadaptor.modelrun.models import ModelRun

blueprint = Blueprint("user", __name__, url_prefix='/api/users',
                      static_folder="../static")


@blueprint.route("/members")
@login_required
def members():
    return render_template("users/member.html")

@blueprint.route("/<int:id>/status")
#@login_required
def get_by_status(id):
    pass

@blueprint.route("/<int:id>/countsbystates")
#@login_required
def count_by_state(id):
    print id
    result = {}
    for state in PROGRESS_STATES:
      result[state] = ModelRun.query.filter_by(user_id=id,progress_state=state).count();
    return jsonify(result)