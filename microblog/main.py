
from flask import redirect, url_for, request, flash, current_app
from collections import UserList
import dateutil.tz
####### here is all
from flask import Blueprint, render_template, abort
import flask_login
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from . import db
from . import model

bp = Blueprint("main", __name__)


# In main.py


@bp.route("/")
def landing():
    # Optional: if already logged in, go straight to index
    if flask_login.current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("main/landing.html")


@bp.route("/index")
@flask_login.login_required
def index():
    # 1. Base Query
    query = db.select(model.Trip)

    # 2. Retrieve Filter Parameters from URL
    dest_id = request.args.get('destination')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    budget = request.args.get('budget')
    filter_type = request.args.get('filter')


    # 3. Apply Filters if they exist
    
    # Destination Filter
    if dest_id:
        # Assumes your Trip model has a 'destination_city_id' or 'city_id' column
        # Check your model.py to see the exact Foreign Key name
        query = query.where(model.Trip.destination_city_id == int(dest_id))

    # Date Range Filters
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.where(model.Trip.start_date >= start_date_obj)
        except ValueError:
            pass  # ignore invalid format instead of crashing

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.where(model.Trip.end_date <= end_date_obj)
        except ValueError:
            pass

    if budget:
        # Convert dropdown string to logic
        if budget == '1':   # Cheap ($)
            # Example: Trips costing less than 20
            query = query.where(model.Trip.budget < 20)
            
        elif budget == '2': # Moderate ($$)
            # Example: Trips between 20 and 45
            query = query.where(model.Trip.budget >= 20, model.Trip.budget <= 45)
            
        elif budget == '3': # Expensive ($$$)
            # Example: Trips costing more than 45
            query = query.where(model.Trip.budget > 45)

    query = query.order_by(model.Trip.status_time.desc())
    if filter_type == 'joined':
        current_user = flask_login.current_user
        query = query.join(model.Trip_participants).where(model.Trip_participants.user_id == current_user.id).order_by(model.Trip.status_time.desc())
    elif filter_type == 'explore':
        current_user = flask_login.current_user
        
        subquery = db.select(model.Trip_participants.trip_id).where(
            model.Trip_participants.user_id == current_user.id
        )
        
        # 2. Filter for Open trips AND IDs that are NOT in the subquery
        query = query.where(
            model.Trip.is_open == True,
            model.Trip.id.not_in(subquery) # This excludes trips you are in
        ).order_by(model.Trip.status_time.desc())
        
    trips = db.session.execute(query).scalars().all()
    
    cities = db.session.execute(db.select(model.City)).scalars().all()

    return render_template("main/index.html", trips=trips, cities=cities)


@bp.route("/explore")
def explore():
    return render_template("main/home.html")


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


@bp.route("/user/<int:user_id>", endpoint="user_profile")
def user_profile(user_id):
    user = db.session.execute(
        db.select(model.User)
        .options(selectinload(model.User.trips_created))
        .where(model.User.id == user_id)
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

    file = request.files.get("profile_picture")
    if file and file.filename:
        from werkzeug.utils import secure_filename
        import os

        allowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in allowed_ext:
            flash("Invalid image type. Please upload JPG, PNG, GIF, or WEBP.", "error")
            return redirect(url_for("main.edit_profile", user_id=user_id))

        # Folder inside static/
        upload_dir = os.path.join(
            current_app.root_path, "static", "uploads", "profile_pictures"
        )
        os.makedirs(upload_dir, exist_ok=True)

        # Unique filename based on user id
        new_filename = f"user_{user_id}{ext}"
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)

        # Save relative path in DB (for use in templates)
        u.profile_picture = f"/static/uploads/profile_pictures/{new_filename}"

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
        
    trip_participants = db.session.execute(
        db.select(model.Trip_participants).where(model.Trip_participants.trip_id == trip_id)
    ).scalars().all()
    trip_participants_count = len(trip_participants) if trip_participants else 0
    
    if trip.max_participants and trip_participants_count >= trip.max_participants:
        trip.is_open = False
        db.session.commit()
    
    
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

    trip_participants = db.session.execute(
        db.select(model.User)
        .join(model.Trip_participants)
        .where(model.Trip_participants.trip_id == trip_id)
    ).scalars().all()
    participants = trip_participants if trip_participants else []

    return render_template(
        "main/trip.html",
        trip=trip,
        is_participant=is_participant,
        is_creator=is_creator,
        has_editing_permissions=has_editing_permissions,
        is_only_editor=is_only_editor,
        participants=participants
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

        # Basic trip information
        title = request.form.get("title")
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
                definite_date = datetime.strptime(definite_date_str, "%Y-%m-%d").date()
        elif date_type == "Range":
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        
        # Other fields
        destination_city_id = request.form.get("destination_city_id")
        # trip_type = request.form.get("trip_type") or None
        # budget = request.form.get("budget")
        # restaurant_name = request.form.get("restaurant_name")
        
        # Attendance and visibility
        # # attendance_type = request.form.get("attendance_type") or "Open for all"
        # visibility = request.form.get("visibility") or "Open"
        max_participants = request.form.get("max_participants")
        
        # is_open checkbox - HTML checkboxes only send value if checked
        # is_open = request.form.get("is_open") is not None
        
        # Create the trip
        new_trip = model.Trip(
            title=title,
            description=description,
            creator_id=creator_id,
            start_date=start_date,
            end_date=end_date,
            definite_date=definite_date,
            destination_city_id=int(destination_city_id) if destination_city_id else None,
            max_participants=int(max_participants) if max_participants else None
        )
        db.session.add(new_trip)
        db.session.flush()  # Get the trip ID before adding stops
        
        stop_indices = set()
        # stops[0][stop_name], stops[0][stop_place], stops[0][stop_status], stops[0][trip_preferences], stops[0][budget], stops[0][stop_type]
        stops_to_create = []


        for i in range(3):  # Only allow 3 stops
            stop_name = request.form.get(f"stops[{i}][stop_name]")
        
            # Skip if stop doesn't exist
            if not stop_name:
                continue
            
            stop_time_str = request.form.get(f"stops[{i}][stop_time]")
            stop_time = None
            if stop_time_str:
                stop_time = datetime.strptime(stop_time_str, "%H:%M").time()
            stop_destination_type = request.form.get(f"stops[{i}][destination_type]")
            # Determine place for first stop
            stop_type = request.form.get(f"stops[{i}][stop_type]")
            if i == 0 and stop_type == "Fixed":
                place = stop_place
            else:
                place = request.form.get(f"stops[{i}][place]")
            
            budget = request.form.get(f"stops[{i}][budget]")

            stops_to_create.append({
                'trip_id': new_trip.id,
                'name': stop_name,
                'place': place,
                'time': stop_time,
                'destination_type': stop_destination_type,
                'notes': request.form.get(f"stops[{i}][notes]"),
                'budget_per_person': float(budget) if budget else None,
                'stop_type': request.form.get(f"stops[{i}][stop_type]"),
                'order': int(request.form.get(f"stops[{i}][stop_order]", i)),
                'stop_status': request.form.get(f"stops[{i}][stop_status]"),
            })
        
        if stops_to_create:
            db.session.bulk_insert_mappings(model.TripStop, stops_to_create)
            
        create_trip_participant = model.Trip_participants(
            trip_id=new_trip.id,
            user_id=creator_id,
            editing_permissions=True
        )
        db.session.add(create_trip_participant)
        db.session.commit()
        
        db.session.commit()
        flash("Trip created successfully!", "success")
        return redirect(url_for("main.trip", trip_id=new_trip.id))

    stop_types = [stop_type for stop_type in model.StopType.enums]
    cities = db.session.execute(db.select(model.City)).scalars().all()
    users = db.session.execute(db.select(model.User)).scalars().all()
    
    return render_template(
        "create_trip.html",
        stop_types=stop_types,
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
    
    if request.method == "POST":
        try:
            # Basic trip information
            trip.title = request.form.get("title")
            trip.description = request.form.get("description")
            
            # Date handling
            date_type = request.form.get("date_type")
            trip.start_date = None
            trip.end_date = None
            trip.definite_date = None
            
            if date_type == "Fixed":
                definite_date_str = request.form.get("definite_date")
                if definite_date_str:
                    trip.definite_date = datetime.strptime(definite_date_str, "%Y-%m-%d").date()
            elif date_type == "Range":
                start_date_str = request.form.get("start_date")
                end_date_str = request.form.get("end_date")
                if start_date_str:
                    trip.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if end_date_str:
                    trip.end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Other fields
            destination_city_id = request.form.get("destination_city_id")
            trip.destination_city_id = int(destination_city_id) if destination_city_id else None
            
            max_participants = request.form.get("max_participants")
            trip.max_participants = int(max_participants) if max_participants else None
            editing_participants_ids = request.form.getlist("edit_permissions")
            # Update participants' editing permissions
            for participant in trip.participants:
                if str(participant.user_id) in editing_participants_ids:
                    participant.editing_permissions = True
                else:
                    participant.editing_permissions = False
            # Delete existing stops
            db.session.execute(
                db.delete(model.TripStop).where(model.TripStop.trip_id == trip.id)
            )
            
            # Add new stops - same logic as create_trip
            stops_to_create = []
            destination_type = request.form.get("destination_type")
            stop_place = request.form.get("stop_place")
            
            for i in range(3):  # Only allow 3 stops
                stop_name = request.form.get(f"stops[{i}][stop_name]")
                
                # Skip if stop doesn't exist
                if not stop_name:
                    continue
                
                stop_time_str = request.form.get(f"stops[{i}][stop_time]")
                stop_time = None
                if stop_time_str:
                    # Handle both HH:MM and HH:MM:SS formats
                    try:
                        stop_time = datetime.strptime(stop_time_str, "%H:%M:%S").time()
                    except ValueError:
                        stop_time = datetime.strptime(stop_time_str, "%H:%M").time()
                
                stop_status = request.form.get(f"stops[{i}][stop_status]")
                stop_type = request.form.get(f"stops[{i}][stop_type]")
                if i == 0 and destination_type == "Fixed":
                    place = stop_place
                else:
                    place = request.form.get(f"stops[{i}][place]")
                
                budget = request.form.get(f"stops[{i}][budget]")
                
                stops_to_create.append({
                    'trip_id': trip.id,
                    'name': stop_name,
                    'place': place,
                    'time': stop_time,
                    'notes': request.form.get(f"stops[{i}][notes]"),
                    'budget_per_person': float(budget) if budget else None,
                    'stop_type': stop_type,
                    'order': int(request.form.get(f"stops[{i}][stop_order]", i)),
                    'stop_status': stop_status
                })
                
            
            if stops_to_create:
                db.session.bulk_insert_mappings(model.TripStop, stops_to_create)
            
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
    users = db.session.execute(db.select(model.User)).scalars().all()
    stop_types = [stop_type for stop_type in model.StopType.enums]
    cities = db.session.execute(db.select(model.City)).scalars().all()
    trip_participants = db.session.execute(
        db.select(model.Trip_participants).where(model.Trip_participants.trip_id == trip_id)
    ).scalars().all()
    stops = db.session.execute(
        db.select(model.TripStop).where(model.TripStop.trip_id == trip_id).order_by(model.TripStop.order)
    ).scalars().all()
    
    date_type = "Range"
    if trip.definite_date:
        date_type = "Fixed"
        
    is_creator = trip.creator_id == flask_login.current_user.id
    has_editing_permissions = is_creator or any(
        p.user_id == flask_login.current_user.id and p.editing_permissions
        for p in trip.participants
    )
    
    
    return render_template(
        "edit_trip.html",
        trip=trip,
        stop_types=stop_types,
        cities=cities,
        users=users,
        stops=stops,
        date_type=date_type,
        participants=trip_participants,
        has_editing_permissions=has_editing_permissions,
        is_creator=is_creator
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
        city_id_raw = request.form.get("city_id")
        date_str = request.form.get("date")
        time_str = request.form.get("time")


        try:
            city_id = int(city_id_raw)
        except (TypeError, ValueError):
            flash("Please select a valid city.", "error")
            return redirect(request.url)

        try:
            meetup_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            meetup_time = datetime.strptime(time_str, "%H:%M").time()
        except (TypeError, ValueError):
            flash("Invalid or missing date/time for the meetup.", "error")
            return redirect(request.url)

        new_meetup = model.Meetups(
            trip_id=trip_id,
            user_id=user.id,
            content=content,
            location=location,
            city_id=city_id,
            date=meetup_date,
            time=meetup_time,
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
    
    trip_participants = db.session.execute(
        db.select(model.Trip_participants).where(model.Trip_participants.trip_id == trip_id)
    ).scalars().all()
    trip_participants_count = len(trip_participants) if trip_participants else 0
    if trip.max_participants and trip_participants_count >= trip.max_participants:
        trip.is_open = False
        db.session.commit()
        
    if trip.is_open == False:
        flash("This trip is closed for new participants.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
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
    for stop in trip.stops:
        if stop.name is None or stop.place is None or stop.date is None or stop.time is None or stop.stop_type is None:
            flash("Must input the following fields for all stops: name, place, date, time, and stop type.", "error")
            return redirect(url_for("main.trip", trip_id=trip.id))
    
    trip.is_finalized = True
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

@bp.route("/close_trip/<int:trip_id>")
@flask_login.login_required
def close_trip(trip_id):
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    trip.is_open = False
    db.session.commit()
    flash("Trip closed successfully!", "success")
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


@bp.route("/message/<int:trip_id>", methods=["POST"])
@flask_login.login_required
def new_message(trip_id):
    content = request.form.get("content")
    current_user = flask_login.current_user
    if not content:
        abort(400, "Message content is required")
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        abort(404, "Trip id {} doesn't exist.".format(trip_id))
    
    trip_participants = db.session.execute(
        db.select(model.Trip_participants)
        .where(model.Trip_participants.trip_id == trip_id)
    ).scalars().all()
    
    is_participant = any(
       participant.user_id == current_user.id
       for participant in trip_participants
    )

    if not is_participant:
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