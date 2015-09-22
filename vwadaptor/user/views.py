from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint("user", __name__, url_prefix='/users',
                      static_folder="../static")


@blueprint.route("/members")
@login_required
def members():
    return render_template("users/member.html")

@blueprint.route("/<int:id>/status")
#@login_required
def get_by_status(id):
    pass