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
            selectinload(model.Trip.comments).selectinload(model.TripComment.author),
            selectinload(model.Trip.stops)
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
        try:
            # Basic trip information
            title = request.form.get("title")
            trip_state = request.form.get("trip_statuses")  # Note: form uses "trip_statuses"
            description = request.form.get("description")
            creator_id = flask_login.current_user.id
            
            # Date handling
            date_type = request.form.get("date_type")
            start_date = None
            end_date = None
            definite_date = None
            
            if date_type == "Fixed":
                definite_date_str = request.form.get("definite_date")
                if definite_date_str:
                    definite_date = datetime.datetime.strptime(definite_date_str, "%Y-%m-%d").date()
            elif date_type == "Range":
                start_date_str = request.form.get("start_date")
                end_date_str = request.form.get("end_date")
                if start_date_str:
                    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if end_date_str:
                    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Destination handling
            destination_type = request.form.get("destination_type")
            destination_city_id = None
            possible_cities = None
            trip_preferences = None
            
            if destination_type == "Fixed":
                dest_id = request.form.get("destination_city_id")
                destination_city_id = int(dest_id) if dest_id else None
            elif destination_type == "Range":
                possible_dest = request.form.getlist("possible_destinations")
                possible_cities = ",".join(possible_dest) if possible_dest else None
            elif destination_type == "Open":
                trip_preferences = request.form.get("trip_preferences")
            
            # Other fields
            departure_city_id = request.form.get("departure_city_id")
            trip_type = request.form.get("trip_type") or None
            budget = request.form.get("budget")
            restaurant_name = request.form.get("restaurant_name")
            
            # Attendance and visibility
            attendance_type = request.form.get("attendance_type") or "Open for all"
            visibility = request.form.get("visibility") or "Open"
            max_participants = request.form.get("max_participants")
            
            # is_open checkbox - HTML checkboxes only send value if checked
            is_open = request.form.get("is_open") is not None
            
            # Create the trip
            new_trip = model.Trip(
                title=title,
                trip_state=trip_state,
                start_date=start_date,
                end_date=end_date,
                definite_date=definite_date,
                description=description,
                destination_city_id=destination_city_id,
                possible_cities=possible_cities,
                trip_preferences=trip_preferences,
                trip_type=trip_type,
                budget=float(budget) if budget else None,
                max_participants=int(max_participants) if max_participants else None,
                is_open=is_open,
                visibility=visibility,
                attendance_type=attendance_type,
                restaurant_name=restaurant_name,
                creator_id=creator_id
            )
            
            db.session.add(new_trip)
            db.session.flush()  # Get the trip ID before adding stops
            
            # Handle food stops
            stop_indices = set()
            for key in request.form.keys():
                if key.startswith("stops[") and key.endswith("][name]"):
                    # Extract index from "stops[0][name]"
                    index = int(key.split('[')[1].split(']')[0])
                    stop_indices.add(index)
            
            for index in sorted(stop_indices):
                stop_name = request.form.get(f"stops[{index}][name]")
                
                # Skip if no name provided
                if not stop_name:
                    continue
                
                stop_place = request.form.get(f"stops[{index}][place]")
                stop_status = request.form.get(f"stops[{index}][status]") or "Just Ideas"
                stop_date_str = request.form.get(f"stops[{index}][date]")
                stop_time_str = request.form.get(f"stops[{index}][time]")
                stop_address = request.form.get(f"stops[{index}][address]")
                stop_budget = request.form.get(f"stops[{index}][budget_per_person]")
                stop_notes = request.form.get(f"stops[{index}][notes]")
                stop_order = request.form.get(f"stops[{index}][order]")
                
                # Parse date and time
                stop_date = None
                if stop_date_str:
                    stop_date = datetime.datetime.strptime(stop_date_str, "%Y-%m-%d").date()
                
                stop_time = None
                if stop_time_str:
                    stop_time = datetime.datetime.strptime(stop_time_str, "%H:%M").time()
                
                new_stop = model.TripStop(
                    trip_id=new_trip.id,
                    name=stop_name,
                    place=stop_place or None,
                    status=stop_status,
                    date=stop_date,
                    time=stop_time,
                    address=stop_address or None,
                    budget_per_person=float(stop_budget) if stop_budget else None,
                    notes=stop_notes or None,
                    order=int(stop_order) if stop_order else index
                )
                db.session.add(new_stop)
            
            # Handle specific people invitations
            if attendance_type == "With Specific People":
                specific_people = request.form.getlist("specific_people")
                for user_id in specific_people:
                    invitation = model.Trip_invitations(
                        trip_id=new_trip.id,
                        user_id=int(user_id)
                    )
                    db.session.add(invitation)
            
            db.session.commit()
            flash("Trip created successfully!", "success")
            return redirect(url_for("main.trip", trip_id=new_trip.id))
            
        except ValueError as e:
            db.session.rollback()
            flash(f"Invalid data format: {str(e)}", "error")
            return redirect(url_for("main.create_trip"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating trip: {str(e)}", "error")
            return redirect(url_for("main.create_trip"))
    
    # GET request - show form
    trip_statuses = ["Just Ideas", "Rough Draft", "Final Plan"]
    trip_types = [trip_type for trip_type in model.TripType.enums]
    attendance_types = [atype for atype in model.AttendanceType.enums]
    visibility_types = [vtype for vtype in model.Visibility.enums]
    
    cities = db.session.execute(db.select(model.City)).scalars().all()
    users = db.session.execute(db.select(model.User)).scalars().all()
    
    return render_template(
        "create_trip.html",
        trip_statuses=trip_statuses,
        trip_types=trip_types,
        attendance_types=attendance_types,
        visibility_types=visibility_types,
        cities=cities,
        users=users
    )
@bp.route("/edit_trip/<int:trip_id>", methods=["GET", "POST"])
@flask_login.login_required
def edit_trip(trip_id):

    trip = db.session.get(model.Trip, trip_id)
    
    if not trip:
        flash("Trip not found.", "error")
        return redirect(url_for("main.index"))
    
    # Verify user is the creator
    if trip.creator_id != flask_login.current_user.id:
        flash("You don't have permission to edit this trip.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    if request.method == "POST":
        try:
            # Basic trip information
            trip.title = request.form.get("title")
            trip.trip_state = request.form.get("trip_statuses")
            trip.description = request.form.get("description")
            
            # Date handling
            date_type = request.form.get("date_type")
            trip.start_date = None
            trip.end_date = None
            trip.definite_date = None
            
            if date_type == "Fixed":
                definite_date_str = request.form.get("definite_date")
                if definite_date_str:
                    trip.definite_date = datetime.datetime.strptime(definite_date_str, "%Y-%m-%d").date()
            elif date_type == "Range":
                start_date_str = request.form.get("start_date")
                end_date_str = request.form.get("end_date")
                if start_date_str:
                    trip.start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if end_date_str:
                    trip.end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Destination handling
            destination_type = request.form.get("destination_type")
            trip.destination_city_id = None
            trip.possible_cities = None
            trip.trip_preferences = None
            
            if destination_type == "Fixed":
                dest_id = request.form.get("destination_city_id")
                trip.destination_city_id = int(dest_id) if dest_id else None
            elif destination_type == "Range":
                possible_dest = request.form.getlist("possible_destinations")
                trip.possible_cities = ",".join(possible_dest) if possible_dest else None
            elif destination_type == "Open":
                trip.trip_preferences = request.form.get("trip_preferences")
            
            # Other fields
            departure_city_id = request.form.get("departure_city_id")
            trip.departure_city_id = int(departure_city_id) if departure_city_id else None
            trip.trip_type = request.form.get("trip_type") or None
            
            budget = request.form.get("budget")
            trip.budget = float(budget) if budget else None
            trip.restaurant_name = request.form.get("restaurant_name")
            
            # Attendance and visibility
            trip.attendance_type = request.form.get("attendance_type") or "Open for all"
            trip.visibility = request.form.get("visibility") or "Open"
            
            max_participants = request.form.get("max_participants")
            trip.max_participants = int(max_participants) if max_participants else None
            
            # is_open checkbox
            trip.is_open = request.form.get("is_open") is not None
            
            # Handle food stops - delete existing and recreate
            # Delete existing stops
            db.session.execute(
                db.delete(model.TripStop).where(model.TripStop.trip_id == trip.id)
            )
            
            # Add new stops
            stop_indices = set()
            for key in request.form.keys():
                if key.startswith("stops[") and key.endswith("][name]"):
                    index = int(key.split('[')[1].split(']')[0])
                    stop_indices.add(index)
            
            for index in sorted(stop_indices):
                stop_name = request.form.get(f"stops[{index}][name]")
                
                if not stop_name:
                    continue
                
                stop_place = request.form.get(f"stops[{index}][place]")
                stop_status = request.form.get(f"stops[{index}][status]") or "Just Ideas"
                stop_date_str = request.form.get(f"stops[{index}][date]")
                stop_time_str = request.form.get(f"stops[{index}][time]")
                stop_address = request.form.get(f"stops[{index}][address]")
                stop_budget = request.form.get(f"stops[{index}][budget_per_person]")
                stop_notes = request.form.get(f"stops[{index}][notes]")
                stop_order = request.form.get(f"stops[{index}][order]")
                
                stop_date = None
                if stop_date_str:
                    stop_date = datetime.datetime.strptime(stop_date_str, "%Y-%m-%d").date()
                
                stop_time = None
                if stop_time_str:
                    stop_time = datetime.datetime.strptime(stop_time_str, "%H:%M").time()
                
                new_stop = model.TripStop(
                    trip_id=trip.id,
                    name=stop_name,
                    place=stop_place or None,
                    status=stop_status,
                    date=stop_date,
                    time=stop_time,
                    address=stop_address or None,
                    budget_per_person=float(stop_budget) if stop_budget else None,
                    notes=stop_notes or None,
                    order=int(stop_order) if stop_order else index
                )
                db.session.add(new_stop)
            
            # Handle specific people invitations
            if trip.attendance_type == "With Specific People":
                # Delete existing invitations
                db.session.execute(
                    db.delete(model.Trip_invitations).where(model.Trip_invitations.trip_id == trip.id)
                )
                
                # Add new invitations
                specific_people = request.form.getlist("specific_people")
                for user_id in specific_people:
                    invitation = model.Trip_invitations(
                        trip_id=trip.id,
                        user_id=int(user_id)
                    )
                    db.session.add(invitation)
            
            db.session.commit()
            flash("Trip updated successfully!", "success")
            return redirect(url_for("main.trip", trip_id=trip.id))
            
        except ValueError as e:
            db.session.rollback()
            flash(f"Invalid data format: {str(e)}", "error")
            return redirect(url_for("main.edit_trip", trip_id=trip_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating trip: {str(e)}", "error")
            return redirect(url_for("main.edit_trip", trip_id=trip_id))
    
    # GET request - show form with existing data
    trip_statuses = ["Just Ideas", "Rough Draft", "Final Plan"]
    trip_types = [trip_type for trip_type in model.TripType.enums]
    attendance_types = [atype for atype in model.AttendanceType.enums]
    visibility_types = [vtype for vtype in model.Visibility.enums]
    
    cities = db.session.execute(db.select(model.City)).scalars().all()
    users = db.session.execute(db.select(model.User)).scalars().all()
    
    # Get existing stops
    stops = db.session.execute(
        db.select(model.TripStop).where(model.TripStop.trip_id == trip_id).order_by(model.TripStop.order)
    ).scalars().all()
    
    # Determine date type
    date_type = "Range"
    if trip.definite_date:
        date_type = "Fixed"
    
    # Determine destination type
    destination_type = "Fixed"
    if trip.possible_cities:
        destination_type = "Range"
    elif trip.trip_preferences:
        destination_type = "Open"
    
    trip_participants = [p.user_id for p in trip.participants]
    return render_template(
        "edit_trip.html",
        trip=trip,
        trip_statuses=trip_statuses,
        trip_types=trip_types,
        attendance_types=attendance_types,
        visibility_types=visibility_types,
        cities=cities,
        users=users,
        stops=stops,
        date_type=date_type,
        destination_type=destination_type,
        trip_participants=trip_participants
    )

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

        if participant.editing_permissions and len(editors) == 1:
            flash("You are the only editor of this trip. Assign another editor before leaving.", "error")
            return redirect(url_for("main.trip", trip_id=trip_id))

        db.session.delete(participant)
        db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))


@bp.route("/finalize_trip/<int:trip_id>")
@flask_login.login_required
def finalize_trip(trip_id):
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    trip.is_final = True
    trip.is_open = False
    db.session.commit()
    flash("Trip finalized successfully!", "success")
    return redirect(url_for("main.trip", trip_id=trip.id))

@bp.route("/cancel_trip/<int:trip_id>")
@flask_login.login_required
def cancel_trip(trip_id):
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    trip.is_cancelled = True
    db.session.commit()
    flash("Trip canceled successfully!", "success")
    return redirect(url_for("main.trip", trip_id=trip.id))

@bp.route("/reopen_trip/<int:trip_id>")
@flask_login.login_required
def reopen_trip(trip_id):
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    trip.is_open = True
    trip.is_cancelled = False
    db.session.commit()
    flash("Trip reopened successfully!", "success")
    return redirect(url_for("main.trip", trip_id=trip.id))


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