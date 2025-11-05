from flask import redirect, url_for, request
from collections import UserList
import datetime
import dateutil.tz
####### here is all
from flask import Blueprint, render_template, abort
import flask_login
from sqlalchemy.orm import selectinload, aliased

from . import db
from . import model

bp = Blueprint("main", __name__)


@bp.route("/")
@flask_login.login_required
def index():
    user = flask_login.current_user
    # trips = [
    #     model.Trip(
    #         id=1, 
    #         creator_id=user.id, 
    #         description="Looking for a good time in Honolulu, Girls only", 
    #         definite_date=datetime.date(2025, 11, 17),
    #         budget=1900
    #     )
    # ]
        # --- Latest top-level posts (already had) ---
    trip_query = (
        db.select(model.Trip)
        .order_by(model.Trip.created_at.desc())
        .limit(10)
    )
    trips = db.session.execute(trip_query).scalars().all()

    return render_template("main/index.html", trips=trips)


@bp.get("/explore")
@flask_login.login_required
def explore():
    trips = db.session.execute(db.select(model.Trip)).scalars().all()
    # If your Trip model has no image_url field yet, you can inject one on the fly:
    for t in trips:
        if not getattr(t, "image_url", None):
            t.image_url = url_for('static', filename='img/image.jpg')
    return render_template("main/home.html", trips=trips)

@bp.route("/home")
def home():
    return render_template("main/home.html")


@bp.route("/user/<int:user_id>")
@flask_login.login_required
def user_profile(user_id):
    # user = flask_login.current_user
    user = db.session.execute(
        db.select(model.User)
        .where(model.User.id == user_id)
    ).scalar_one_or_none() 
    if not user:
        abort(404)
    return render_template("main/profile.html", user=user)

# Optional: accept the POST to simulate an update (no DB persistence)
@bp.route("/user/<int:user_id>/edit", methods=["POST"])
def edit_user(user_id):
    # read form values (just to demonstrate)
    email = (request.form.get("email") or "").strip()
    name = (request.form.get("name") or "").strip()
    description = request.form.get("description") or ""
    # pretend we saved:
    flash("Profile updated (demo). No DB persistence yet.", "success")
    return redirect(url_for("main.user_profile", user_id=user_id))

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

@bp.route("/message", methods=["POST"])
@flask_login.login_required
def new_message():
    content = request.form.get("content")
    trip_id = request.form.get("trip_id")  # Get trip_id from form
    
    if not content:
        abort(400, "Message content is required")
    
    if not trip_id:
        abort(400, "Trip ID is required")
    
    # Verify the trip exists
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    
    # Verify user is a participant of the trip (add this security check)
    # You'll need to implement this based on your Trip-User relationship
    # if not trip.participants.filter(id=flask_login.current_user.id).first():
    #     abort(403, "You are not a participant of this trip.")

    # Create the TripComment
    comment = model.TripComment(
        content=content,
        author_id=flask_login.current_user.id,
        trip_id=trip_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # Redirect back to the trip page
    return redirect(url_for("main.trip", trip_id=trip_id))