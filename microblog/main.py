from collections import UserList
import datetime
import dateutil.tz
####### here is all
from flask import Blueprint, render_template, abort
import flask_login
#

from . import db
from . import model

bp = Blueprint("main", __name__)


@bp.route("/")
@flask_login.login_required
def index():
    user = model.User(id=1, email="mary@example.com", name="mary", password="dummy", description="")
    trips = [
        model.Trip(id=1, user_id=user.id, departure="Odessa, Wa"),
        model.Trip(id=2, user_id=user.id, departure="Israel"),
    ]
    return render_template("main/index.html", trip=trips)

@bp.route("/user/<int:user_id>")
@flask_login.login_required
def user_profile(user_id):
    user = model.User(id=1, email = "mar@example.com", name = "mary", password = "dummy", description = "")
    if not user:
        abort(404)
    return render_template("main/profile.html", user = user)

@bp.route("/post/<int:post_id>")
@flask_login.login_required
def post(post_id):
    trip = db.session.get(model.Trip, trip.id, trip.departure)
    if not post:
        abort(404, "Post id {} doesn't exist.".format(id))
    # Get responses to this post
    # query = db.select(model.Trip)
    # responses = db.session.execute(query).scalars().all()
    
    return render_template("main/posts.html", trip=trip)
