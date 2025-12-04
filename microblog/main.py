
from flask import redirect, url_for, request, flash, current_app, app
from collections import UserList
import dateutil.tz
####### here is all
from flask import Blueprint, render_template, abort
import flask_login
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.exc import IntegrityError
#from datetime import datetime
import datetime as dt
from . import db
from . import model
from sqlalchemy import or_
CITY_IMAGES =  {
        "Alicante": "https://images.unsplash.com/photo-1680537732160-01750bae5217?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Barcelona": "https://images.unsplash.com/photo-1630219694734-fe47ab76b15e?q=80&w=1504&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Bilbao": "https://images.unsplash.com/photo-1566993850427-6324a91bbd32?q=80&w=1780&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Córdoba": "https://images.unsplash.com/photo-1707583056849-4c8a7fb5570d?q=80&w=1742&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Granada": "https://images.unsplash.com/photo-1620677368158-32b1293fac36?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Madrid": "https://images.unsplash.com/photo-1543783207-ec64e4d95325?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Málaga": "https://images.unsplash.com/photo-1641667710644-fb8a6abf2a06?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Murcia": "https://plus.unsplash.com/premium_photo-1697729491014-0da08900c12c?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Salamanca": "https://plus.unsplash.com/premium_photo-1697730517637-a5c2f354439b?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "San Sebastián": "https://plus.unsplash.com/premium_photo-1697729411955-2b33ce7c819f?q=80&w=1548&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Santander": "https://plus.unsplash.com/premium_photo-1697729454180-c9d49ba1fe82?q=80&w=1548&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Seville": "https://images.unsplash.com/photo-1688404808661-92f72f2ea258?q=80&w=1752&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Toledo": "https://images.unsplash.com/photo-1468412526475-8cc70299f66f?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Valencia": "https://images.unsplash.com/photo-1565768502719-571073a68b4c?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Zaragoza": "https://images.unsplash.com/photo-1612072451833-bb858853aaf5?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    }


bp = Blueprint("main", __name__)



# Controller for the main landing page
@bp.route("/")
def landing():
    # Optional: if already logged in, go straight to index
    if flask_login.current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("main/landing.html")


# Controller for the index - Trip Dashboard
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
            start_date_obj = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.where(model.Trip.start_date >= start_date_obj)
        except ValueError:
            pass  # ignore invalid format instead of crashing

    if end_date:
        try:
            end_date_obj = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
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

    current_user = flask_login.current_user

    # Subquery: all trip_ids where current user participates
    participation_subq = (
        db.select(model.Trip_participants.trip_id)
        .where(model.Trip_participants.user_id == current_user.id)
    )

    if filter_type == "joined":
        # Joined trips — user is participant (open OR closed)
        query = query.where(model.Trip.id.in_(participation_subq))

    elif filter_type == "explore":
        # Explore — open trips NOT joined by the user
        query = query.where(
            model.Trip.is_open.is_(True),
            model.Trip.is_cancelled.is_(False),
            model.Trip.id.not_in(participation_subq)
        )

    else:
        # All Trips (dashboard)
        # - Show open trips to everyone
        # - Plus closed trips where the user is a participant
        query = query.where(
            or_(
                model.Trip.is_open.is_(True),
                model.Trip.id.in_(participation_subq)
            ),
            model.Trip.is_cancelled.is_(False)
        )


    query = query.order_by(model.Trip.status_time.desc())
    trips = db.session.execute(query).scalars().all()
    cities = db.session.execute(db.select(model.City)).scalars().all()
    return render_template("main/index.html", trips=trips, cities=cities, city_images=CITY_IMAGES)



# Controller for the explore page (different landing)
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



# Controller for the user profile
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



    return render_template("main/user_watch.html", user=user, is_owner=is_owner, city_images=CITY_IMAGES)

# Controller for editing the profile after authentication
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


# Controller to render a trip
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

    if trip.is_cancelled:
        trip_status = "cancelled"
    elif not trip.is_open:
        trip_status = "closed"
    elif trip.is_finalized:
        trip_status = "finalized"
    else:
        trip_status = "open"

        # Determine participant edit/join permissions
    can_join = trip.is_open and not is_participant
    can_edit = has_editing_permissions and trip.is_open and not trip.is_cancelled

    return render_template(
        "main/trip.html",
        trip=trip,
        is_participant=is_participant,
        is_creator=is_creator,
        has_editing_permissions=has_editing_permissions,
        is_only_editor=is_only_editor,
        participants=participants,
        city_images = CITY_IMAGES,
        trip_status=trip_status,
        can_join=can_join,
        can_edit=can_edit
    )

# controller for the index (rendering all trips)
@bp.route("/trips")
@flask_login.login_required
def trips():
    trips = db.session.execute(db.select(model.Trip)).scalars().all()
    return render_template("trips_template.html", trips= trips)


# Controller to create a trip
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
                definite_date = dt.datetime.strptime(definite_date_str, "%Y-%m-%d").date()
        elif date_type == "Range":
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")
            if start_date_str:
                start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if end_date_str:
                end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        
        # Other fields
        destination_city_id = request.form.get("destination_city_id")
        # trip_type = request.form.get("trip_type") or None
        budget_raw = request.form.get("budget")
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
            max_participants=int(max_participants) if max_participants else None,
            budget=float(budget_raw) if budget_raw else None
        )
        db.session.add(new_trip)
        db.session.flush()  # Get the trip ID before adding stops
        
        stop_indices = set()
        # stops[0][stop_name], stops[0][stop_place], stops[0][stop_status], stops[0][trip_preferences], stops[0][budget], stops[0][stop_type]


        # --- STOP HANDLING (max 3) ---
        MAX_STOPS = 3
        stops_to_create = []

        # Get destination type (Fixed / Open) and stop_place for first stop logic
        destination_type = request.form.get("destination_type")
        stop_place = request.form.get("stop_place")

        for i in range(MAX_STOPS):
            stop_name = request.form.get(f"stops[{i}][stop_name]")
            if not stop_name:
                continue  # skip empty stops

            stop_time_str = request.form.get(f"stops[{i}][stop_time]")
            stop_time = None
            if stop_time_str:
                try:
                    stop_time = dt.datetime.strptime(stop_time_str, "%H:%M:%S").time()
                except ValueError:
                    stop_time = dt.datetime.strptime(stop_time_str, "%H:%M").time()

            stop_status = request.form.get(f"stops[{i}][stop_status]")
            stop_type = request.form.get(f"stops[{i}][stop_type]")

            # Determine place for first stop
            if i == 0 and destination_type == "Fixed":
                place = stop_place
            else:
                place = request.form.get(f"stops[{i}][place]")

            budget = request.form.get(f"stops[{i}][budget]")
            notes = request.form.get(f"stops[{i}][notes]")

            stops_to_create.append({
                'trip_id': new_trip.id,
                'name': stop_name,
                'place': place,
                'time': stop_time,
                'notes': notes,
                'budget_per_person': float(budget) if budget else None,
                'stop_type': stop_type,
                'order': int(request.form.get(f"stops[{i}][stop_order]", i)),
                'stop_status': stop_status
            })

        if stops_to_create:
            db.session.bulk_insert_mappings(model.TripStop, stops_to_create)

            # Recalculate trip budget from stops
            total_budget = sum(stop.get('budget_per_person') or 0 for stop in stops_to_create)
            new_trip.budget = total_budget

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
        users=users,
        city_images = CITY_IMAGES
    )


# Controller to edit a trip
@bp.route("/edit_trip/<int:trip_id>", methods=["GET", "POST"])
@flask_login.login_required
def edit_trip(trip_id):
    trip = db.session.get(model.Trip, trip_id)
    if not trip:
        flash("Trip not found.", "error")
        return redirect(url_for("main.index"))

    MAX_STOPS = 3

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
                    trip.definite_date = dt.datetime.strptime(definite_date_str, "%Y-%m-%d").date()
            elif date_type == "Range":
                start_date_str = request.form.get("start_date")
                end_date_str = request.form.get("end_date")
                if start_date_str:
                    trip.start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if end_date_str:
                    trip.end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # Other fields
            destination_city_id = request.form.get("destination_city_id")
            trip.destination_city_id = int(destination_city_id) if destination_city_id else None

            max_participants = request.form.get("max_participants")
            trip.max_participants = int(max_participants) if max_participants else None

            # Editing permissions
            editing_participants_ids = request.form.getlist("edit_permissions")
            for participant in trip.participants:
                participant.editing_permissions = str(participant.user_id) in editing_participants_ids

                # --- STOP HANDLING (max 3 stops) ---
                stops_to_create = []
                destination_type = request.form.get("destination_type")
                stop_place = request.form.get("stop_place")

                # Dynamically detect number of stops submitted
                stop_keys = [key for key in request.form.keys() if key.startswith("stops[")]
                if stop_keys:
                    max_index = max(int(k.split("[")[1].split("]")[0]) for k in stop_keys)
                    num_stops = min(max_index + 1, MAX_STOPS)  # 🔒 enforce limit
                else:
                    num_stops = 0

                for i in range(num_stops):
                    stop_name = request.form.get(f"stops[{i}][stop_name]")
                    if not stop_name:
                        continue

                    stop_time_str = request.form.get(f"stops[{i}][stop_time]")
                    stop_time = None
                    if stop_time_str:
                        try:
                            stop_time = dt.datetime.strptime(stop_time_str, "%H:%M:%S").time()
                        except ValueError:
                            stop_time = dt.datetime.strptime(stop_time_str, "%H:%M").time()

                    stop_status = request.form.get(f"stops[{i}][stop_status]")
                    stop_type = request.form.get(f"stops[{i}][stop_type]")

                    if i == 0 and destination_type == "Fixed":
                        place = stop_place
                    else:
                        place = request.form.get(f"stops[{i}][place]")

                    budget = request.form.get(f"stops[{i}][budget]")
                    notes = request.form.get(f"stops[{i}][notes]")

                    stops_to_create.append({
                        "trip_id": trip.id,
                        "name": stop_name,
                        "place": place,
                        "time": stop_time,
                        "notes": notes,
                        "budget_per_person": float(budget) if budget else None,
                        "stop_type": stop_type,
                        "order": int(request.form.get(f"stops[{i}][stop_order]", i)),
                        "stop_status": stop_status
                    })

                # 🟢 Delete and recreate stops only if we have some
                if stops_to_create:
                    db.session.execute(
                        db.delete(model.TripStop).where(model.TripStop.trip_id == trip.id)
                    )
                    db.session.bulk_insert_mappings(model.TripStop, stops_to_create)

                    # Recalculate trip budget
                    total_budget = sum(stop.get("budget_per_person") or 0 for stop in stops_to_create)
                    trip.budget = total_budget

                db.session.commit()
                flash("Trip updated successfully!", "success")
                return redirect(url_for("main.trip", trip_id=trip.id))

        except ValueError as e:
            db.session.rollback()
            flash(f"Invalid data format: {str(e)}", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating trip: {str(e)}", "error")

        return redirect(url_for("main.edit_trip", trip_id=trip_id))

    # GET request
    users = db.session.execute(db.select(model.User)).scalars().all()
    stop_types = [stop_type for stop_type in model.StopType.enums]
    cities = db.session.execute(db.select(model.City)).scalars().all()
    trip_participants = db.session.execute(
        db.select(model.Trip_participants).where(model.Trip_participants.trip_id == trip_id)
    ).scalars().all()
    stops = db.session.execute(
        db.select(model.TripStop).where(model.TripStop.trip_id == trip_id).order_by(model.TripStop.order)
    ).scalars().all()

    date_type = "Fixed" if trip.definite_date else "Range"

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
        is_creator=is_creator,
    )



# Controller to create a meetup
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
            meetup_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
            meetup_time = dt.datetime.strptime(time_str, "%H:%M").time()
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


# Controller to join a trip
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


# Controller to leave a trip
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


# Controller to finalize trip
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


# Controller to cancel a trip
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


# Controller to close a trip
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


# Controller to re-open trip
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


# Controller to create a new message
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