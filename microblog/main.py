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
        model.Trip(id=1, user = user, departure="Odessa, Wa", destination = "Maui, Hawaii", status = "In Planning", 
        text = "Looking for a good time in Honolulu, Girls only", possible_dates = datetime.date(2025, 11, 17),
        budget = 1900)
        # model.Trip(id=2, user_id=user.id, departure="Israel"),
    ]
    return render_template("main/index.html", trips=trips)

@bp.route("/user/<int:user_id>")
@flask_login.login_required
def user_profile(user_id):
    user = model.User(id=1, email = "mar@example.com", name = "mary", password = "dummy", description = "")
    if not user:
        abort(404)
    return render_template("main/profile.html", user = user)

@bp.route("/trip/<int:trip_id>")
@flask_login.login_required
def trip(trip_id):
    # Query the trip from database using the trip_id parameter
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    return render_template("main/trip.html", trip=trip)

@bp.route("/trips")
@flask_login.login_required
def trips():
    trips = db.session.execute(db.select(model.Trip)).scalars().all()
    return render_template("trips_template.html", trips= trips)