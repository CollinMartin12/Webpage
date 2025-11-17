from flask import redirect, url_for, request, flash
from collections import UserList
import datetime
import dateutil.tz
####### here is all
from flask import Blueprint, render_template, abort
import flask_login
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.exc import IntegrityError

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
        .order_by(model.Trip.status_time.desc())
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
@flask_login.login_required
def home():
    user = flask_login.current_user

    # Trips where the user is a participant
    my_trips = (
        db.session.execute(
            db.select(model.Trip)
            .join(model.Trip_participants)
            .where(model.Trip_participants.user_id == user.id)
        )
        .scalars()
        .all()
    )

    # All open trips
    open_trips = (
        db.session.execute(
            db.select(model.Trip)
            .where(model.Trip.is_open == True)
        )
        .scalars()
        .all()
    )

    return render_template(
        "main/home.html",
        my_trips=my_trips,
        open_trips=open_trips
    )


@bp.route("/user/<int:user_id>", endpoint="user_profile")  # keep endpoint name for existing links
def user_profile(user_id):

    user = db.session.execute(
        db.select(model.User).where(model.User.id == user_id)
    ).scalar_one_or_none()
    if not user:
        abort(404)

    is_owner = (
        flask_login.current_user.is_authenticated
        and int(flask_login.current_user.get_id()) == user.id
    )

    return render_template("main/user_watch.html", user=user, is_owner=is_owner)


@bp.get("/user/<int:user_id>/edit")
@flask_login.login_required
def edit_profile(user_id):

    user = db.session.get(model.User, user_id)
    if not user:
        abort(404)

    if int(flask_login.current_user.get_id()) != user.id:
        # Non-owners: back to read-only
        return redirect(url_for("main.user_profile", user_id=user.id))

    return render_template("main/profile.html", user=user)


@bp.post("/user/<int:user_id>/edit")
@flask_login.login_required
def edit_user(user_id):

    try:
        current_id = int(flask_login.current_user.get_id())
    except (TypeError, ValueError):
        abort(401)
    if current_id != int(user_id):
        abort(403)

    u = db.session.get(model.User, user_id)
    if not u:
        abort(404)

    email = (request.form.get("email") or "").strip()
    name = (request.form.get("name") or "").strip()
    desc = request.form.get("description") or ""
    pw = request.form.get("password") or ""
    pw2 = request.form.get("password2") or ""

    # Basic validation
    if not email or not name:
        flash("Email and name are required.", "error")
        return redirect(url_for("main.edit_profile", user_id=user_id))

    if pw or pw2:
        if pw != pw2:
            flash("Passwords do not match.", "error")
            return redirect(url_for("main.edit_profile", user_id=user_id))
        # TODO: hash in production
        u.password = pw

    # Apply changes
    u.email = email
    u.name = name
    u.description = desc

    # Commit with unique email handling
    try:
        db.session.commit()
        flash("Profile updated.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("That email is already in use.", "error")

    return redirect(url_for("main.user_profile", user_id=user_id))





@bp.route("/trip/<int:trip_id>")
@flask_login.login_required
def trip(trip_id):
    trip = db.session.execute(
        db.select(model.Trip)
        .options(
            selectinload(model.Trip.participants),
            selectinload(model.Trip.comments).selectinload(model.TripComment.author)
        )
        .where(model.Trip.id == trip_id)
    ).scalar_one_or_none()
    
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    
    user = flask_login.current_user
    has_editing_permissions = False
    is_participant = any(
        participant.user_id == user.id for participant in trip.participants
    )
    is_creator = trip.creator_id == user.id

    has_editing_permissions = is_creator or any(
        participant.user_id == user.id and participant.editing_permissions 
        for participant in trip.participants
    )

    # Count how many participants have editing permissions
    editor_count = sum(1 for p in trip.participants if p.editing_permissions)

    # Determine if the current user is the only editor
    is_only_editor = has_editing_permissions and editor_count == 1

    return render_template(
        "main/trip.html",
        trip=trip,
        is_participant=is_participant,
        is_creator=is_creator,
        has_editing_permissions=has_editing_permissions,
        is_only_editor=is_only_editor
    )





@bp.route("/trips")
@flask_login.login_required
def trips():
    trips = db.session.execute(db.select(model.Trip)).scalars().all()
    return render_template("trips_template.html", trips= trips)


@bp.route("/create_trip", methods=["GET", "POST"])
@flask_login.login_required
def create_trip():
    
    if request.method == "POST":
        # Get form data
        departure_city_id = request.form.get("departure_city_id") or None
        departure_neighborhood_id = request.form.get("departure_neighborhood_id") or None
        destination_city_id = request.form.get("destination_city_id")
        destination_neighborhood_id = request.form.get("destination_neighborhood_id") or None
        trip_type_id = request.form.get("trip_type_id") or None
        description = request.form.get("description")
        restaurant_name = request.form.get("restaurant_name") or None
        definite_date = request.form.get("definite_date")
        budget = request.form.get("budget")
        picture = request.form.get("picture") or None
        max_participants = request.form.get("max_participants")
        is_open = request.form.get("is_open") == "on"

        new_trip = model.Trip(
            creator_id=flask_login.current_user.id,
            departure_city_id=int(departure_city_id) if departure_city_id else None,
            departure_neighborhood_id=int(departure_neighborhood_id) if departure_neighborhood_id else None,
            destination_city_id=int(destination_city_id) if destination_city_id else None,
            destination_neighborhood_id=int(destination_neighborhood_id) if destination_neighborhood_id else None,
            trip_type_id=int(trip_type_id) if trip_type_id else None,
            description=description,
            restaurant_name=restaurant_name,
            definite_date=datetime.datetime.strptime(definite_date, "%Y-%m-%d").date() if definite_date else None,
            budget=float(budget) if budget else None,
            picture=picture,
            max_participants=int(max_participants) if max_participants else None,
            is_open=is_open,
            created_at=datetime.datetime.now(dateutil.tz.UTC),
            status_time=datetime.datetime.now(dateutil.tz.UTC)
        )
        db.session.add(new_trip)
        db.session.commit()
        flash("Trip created successfully!", "success")

        # THEN ADD THE CREATOR AS A PARTICIPANT WITH EDITING PERMISSIONS
        new_participant = model.Trip_participants(
            trip_id=new_trip.id,
            user_id=flask_login.current_user.id,
            editing_permissions=True
        )
        db.session.add(new_participant)
        db.session.commit()
        return redirect(url_for("main.trip", trip_id=new_trip.id))
    
    cities = db.session.execute(db.select(model.City)).scalars().all()
    neighborhoods = db.session.execute(db.select(model.Neighborhood)).scalars().all()
    trip_types = db.session.execute(db.select(model.TripType)).scalars().all()
    
    return render_template("create_trip.html", cities=cities, neighborhoods=neighborhoods, trip_types=trip_types)


@bp.route("/edit_trip/<int:trip_id>", methods=["GET", "POST"])
@flask_login.login_required
def edit_trip(trip_id):
    trip = db.session.execute(
        db.select(model.Trip)
        .options(selectinload(model.Trip.participants))
        .where(model.Trip.id == trip_id)
    ).scalar_one_or_none()
    
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    
    user = flask_login.current_user
    
    # Check if user has editing permissions
    is_creator = trip.creator_id == user.id
    has_editing_permissions = is_creator or any(
        p.user_id == user.id and p.editing_permissions for p in trip.participants
    )
    
    if not has_editing_permissions:
        flash("You don't have permission to edit this trip.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    if request.method == "POST":
        # Get form data
        departure_city_id = request.form.get("departure_city_id") or None
        departure_neighborhood_id = request.form.get("departure_neighborhood_id") or None
        destination_city_id = request.form.get("destination_city_id")
        destination_neighborhood_id = request.form.get("destination_neighborhood_id") or None
        trip_type_id = request.form.get("trip_type_id") or None
        description = request.form.get("description")
        restaurant_name = request.form.get("restaurant_name") or None
        definite_date = request.form.get("definite_date")
        budget = request.form.get("budget")
        picture = request.form.get("picture") or None
        max_participants = request.form.get("max_participants")
        is_open = request.form.get("is_open") == "on"

        # Update trip fields
        trip.departure_city_id = int(departure_city_id) if departure_city_id else None
        trip.departure_neighborhood_id = int(departure_neighborhood_id) if departure_neighborhood_id else None
        trip.destination_city_id = int(destination_city_id) if destination_city_id else None
        trip.destination_neighborhood_id = int(destination_neighborhood_id) if destination_neighborhood_id else None
        trip.trip_type_id = int(trip_type_id) if trip_type_id else None
        trip.description = description
        trip.restaurant_name = restaurant_name
        trip.definite_date = datetime.datetime.strptime(definite_date, "%Y-%m-%d").date() if definite_date else None
        trip.budget = float(budget) if budget else None
        trip.picture = picture
        trip.max_participants = int(max_participants) if max_participants else None
        trip.is_open = is_open
        
        if is_creator:
            for participant in trip.participants:
                permission_field = f"editing_perm_{participant.user_id}"
                new_permission = permission_field in request.form
                participant.editing_permissions = new_permission
                
        db.session.commit()
        flash("Trip updated successfully!", "success")
        return redirect(url_for("main.trip", trip_id=trip.id))
    
    cities = db.session.execute(db.select(model.City)).scalars().all()
    neighborhoods = db.session.execute(db.select(model.Neighborhood)).scalars().all()
    trip_types = db.session.execute(db.select(model.TripType)).scalars().all()

    return render_template("edit_trip.html", trip=trip, cities=cities, neighborhoods=neighborhoods, trip_types=trip_types, is_creator=is_creator, has_editing_permissions=has_editing_permissions)



@bp.route("/trip/<int:trip_id>/meetup/create", methods=["GET", "POST"])
@flask_login.login_required
def create_meetup(trip_id):
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip not found")

    user = flask_login.current_user

    # Check editing permissions
    is_creator = trip.creator_id == user.id
    has_editing_permissions = is_creator or any(
        p.user_id == user.id and p.editing_permissions
        for p in trip.participants
    )

    if not has_editing_permissions:
        flash("You do not have permission to create meetups for this trip.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))

    if request.method == "POST":
        content = request.form.get("content")
        location = request.form.get("location")
        city_id = request.form.get("city_id")
        date = request.form.get("date")
        time = request.form.get("time")

        new_meetup = model.Meetups(
            trip_id=trip_id,
            user_id=user.id,
            content=content,
            location=location,
            city_id=int(city_id),
            date=datetime.datetime.strptime(date, "%Y-%m-%d").date(),
            time=datetime.datetime.strptime(time, "%H:%M").time(),
            status="PLANNING"
        )

        db.session.add(new_meetup)
        db.session.commit()

        flash("Meetup created successfully!", "success")
        return redirect(url_for("main.trip", trip_id=trip_id))

    # For dropdown list
    cities = db.session.execute(db.select(model.City)).scalars().all()

    return render_template("main/meetup.html", trip=trip, cities=cities)



@bp.route("/join/<int:trip_id>")
@flask_login.login_required
def join_trip(trip_id):
    user = flask_login.current_user
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    participant = db.session.execute(
        db.select(model.Trip_participants)
        .where(
            model.Trip_participants.trip_id == trip_id,
            model.Trip_participants.user_id == user.id
        )
    ).scalar_one_or_none()
    if participant:
        participant.editing_permissions = True
    else:
        new_participant = model.Trip_participants(
            trip_id=trip_id,
            user_id=user.id,
            editing_permissions=True
        )
        db.session.add(new_participant)
    db.session.commit()
    trips = db.session.execute(db.select(model.Trip)).scalars().all()
    return redirect(url_for("main.trip", trip_id=trip_id))


@bp.route("/leave/<int:trip_id>")
@flask_login.login_required
def leave_trip(trip_id):
    user = flask_login.current_user
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    participant = db.session.execute(
        db.select(model.Trip_participants)
        .where(
            model.Trip_participants.trip_id == trip_id,
            model.Trip_participants.user_id == user.id
        )
    ).scalar_one_or_none()
    if participant:

        # Count how many editors the trip has
        editors = db.session.execute(
            db.select(model.Trip_participants)
            .where(
                model.Trip_participants.trip_id == trip_id,
                model.Trip_participants.editing_permissions == True
            )
        ).scalars().all()

        # If user is the only editor, prevent leaving
        if participant.editing_permissions and len(editors) == 1:
            flash("You are the only editor of this trip. Assign another editor before leaving.", "error")
            return redirect(url_for("main.trip", trip_id=trip_id))

        db.session.delete(participant)
        db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))



@bp.route("/message", methods=["POST"])
@flask_login.login_required
def new_message():
    content = request.form.get("content")
    trip_id = request.form.get("trip_id")  # Get trip_id from form
    current_user = flask_login.current_user
    if not content:
        abort(400, "Message content is required")
    
    if not trip_id:
        abort(400, "Trip ID is required")
    
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    
    trip_participants = db.session.execute(
        db.select(model.Trip_participants)
        .where(model.Trip_participants.trip_id == trip_id)
    ).scalars().all()

    if current_user not in [participant.user for participant in trip_participants]:
        flash("You must be a participant of the trip to comment.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))


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