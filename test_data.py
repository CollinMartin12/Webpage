#!/usr/bin/env python3
"""
Test Data Script for Microblog Application (with Trip_invitations)
==================================================================
This script inserts test data into all tables to verify the database schema is working correctly.
Run this script after your database is initialized.

Usage:
  python test_data.py
  python test_data.py clear   # to wipe test data
"""

from datetime import date, time

from microblog import create_app
from microblog.model import (
    db,
    User,
    City,
    Neighborhood,
    Trip,
    TripStop,
    Interest,
    FollowingAssociation,
    Trip_participants,
    Trip_invitations,
    Meetups,
    TripComment,
)


def create_test_data():
    app = create_app()
    with app.app_context():
        print("🧪 Creating test data...")
        
        # First, clear any existing test data to avoid duplicates
        print("🧹 Clearing existing data first...")
        try:
            TripComment.query.delete()
            Meetups.query.delete()
            TripStop.query.delete()
            Trip_participants.query.delete()
            Trip_invitations.query.delete()
            Trip.query.delete()
            FollowingAssociation.query.delete()
            Interest.query.delete()
            User.query.delete()
            Neighborhood.query.delete()
            City.query.delete()
            db.session.commit()
            print("✅ Cleared existing data")
        except Exception as e:
            print(f"⚠️  Note: Error clearing data (probably first run): {e}")
            db.session.rollback()

        try:
            # 1. Create Cities (check for existing first)
            print("📍 Creating cities...")
            city_names = ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"]
            cities = {}
            
            for city_name in city_names:
                existing_city = City.query.filter_by(name=city_name).first()
                if existing_city:
                    cities[city_name.lower()] = existing_city
                    print(f"   City '{city_name}' already exists")
                else:
                    new_city = City(name=city_name)
                    db.session.add(new_city)
                    db.session.flush()  # Get the ID without committing
                    cities[city_name.lower()] = new_city
                    print(f"   Created city '{city_name}'")
            
            db.session.commit()
            print(f"✅ Total cities in database: {City.query.count()}")
            
            # Create references to cities for later use
            madrid = cities['madrid']
            barcelona = cities['barcelona']
            valencia = cities['valencia']
            seville = cities['seville']
            bilbao = cities['bilbao']

            # 2. Create Neighborhoods (check for existing first)
            print("🏘️ Creating neighborhoods...")
            neighborhood_names = ["Centro", "Malasaña", "Chueca", "Gràcia", "Eixample", "Ciutat Vella"]
            neighborhoods = {}
            
            for neighborhood_name in neighborhood_names:
                existing_neighborhood = Neighborhood.query.filter_by(name=neighborhood_name).first()
                if existing_neighborhood:
                    neighborhoods[neighborhood_name.lower().replace('ñ', 'n').replace('à', 'a')] = existing_neighborhood
                    print(f"   Neighborhood '{neighborhood_name}' already exists")
                else:
                    new_neighborhood = Neighborhood(name=neighborhood_name)
                    db.session.add(new_neighborhood)
                    db.session.flush()  # Get the ID without committing
                    neighborhoods[neighborhood_name.lower().replace('ñ', 'n').replace('à', 'a')] = new_neighborhood
                    print(f"   Created neighborhood '{neighborhood_name}'")
            
            db.session.commit()
            print(f"✅ Total neighborhoods in database: {Neighborhood.query.count()}")
            
            # Create references to neighborhoods for later use
            centro = neighborhoods['centro']
            malasana = neighborhoods['malasana']
            chueca = neighborhoods['chueca']
            gracia = neighborhoods['gracia']
            eixample = neighborhoods['eixample']
            ciutat_vella = neighborhoods['ciutat vella']

            # 3. Create Users (check for existing first)
            print("👥 Creating users...")
            user_data = [
                ("alice@example.com", "Alice Johnson", "hashed_password_123", "Food lover from Madrid", madrid.id, centro.id, None),
                ("bob@example.com", "Bob Martinez", "hashed_password_456", "Chef exploring Spanish cuisine", barcelona.id, gracia.id, "/static/images/bob_profile.jpg"),
                ("carol@example.com", "Carol Smith", "hashed_password_789", "Travel blogger and foodie", valencia.id, None, None),
                ("david@example.com", "David Rodriguez", "hashed_password_101", "Local food guide", None, None, "/static/images/david_profile.jpg"),
            ]
            
            users = []
            for email, name, password, description, city_id, neighborhood_id, profile_picture in user_data:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    users.append(existing_user)
                    print(f"   User '{email}' already exists")
                else:
                    new_user = User(
                        email=email,
                        name=name,
                        password=password,
                        description=description,
                        city_id=city_id,
                        neighborhood_id=neighborhood_id,
                        profile_picture=profile_picture,
                    )
                    db.session.add(new_user)
                    db.session.flush()  # Get the ID without committing
                    users.append(new_user)
                    print(f"   Created user '{email}'")
            
            db.session.commit()
            print(f"✅ Total users in database: {User.query.count()}")
            
            # Create references to users for later use
            user1, user2, user3, user4 = users

            # 4. Create Interests
            print("💭 Creating interests...")
            interest1 = Interest(user_id=user1.id, interest="Italian cuisine")
            interest2 = Interest(user_id=user1.id, interest="Wine tasting")
            interest3 = Interest(user_id=user2.id, interest="Street food")
            interest4 = Interest(user_id=user3.id, interest="Vegetarian food")
            interest5 = Interest(user_id=user4.id, interest="Michelin starred restaurants")

            db.session.add_all(
                [interest1, interest2, interest3, interest4, interest5]
            )
            db.session.commit()
            print(f"✅ Created {Interest.query.count()} interests")

            # 5. Create Following relationships
            print("👤 Creating following relationships...")
            follow1 = FollowingAssociation(follower_id=user1.id, followed_id=user2.id)
            follow2 = FollowingAssociation(follower_id=user1.id, followed_id=user3.id)
            follow3 = FollowingAssociation(follower_id=user2.id, followed_id=user1.id)
            follow4 = FollowingAssociation(follower_id=user3.id, followed_id=user4.id)

            db.session.add_all([follow1, follow2, follow3, follow4])
            db.session.commit()
            print(
                f"✅ Created {FollowingAssociation.query.count()} following relationships"
            )

            # 6. Create Trips (matching new Trip model)
            print("✈️ Creating trips...")
            trip1 = Trip(
                title="Barcelona Food Adventure",
                creator_id=user1.id,
                destination_city_id=barcelona.id,
                possible_cities="Barcelona, Girona",
                # timing
                start_date=date(2025, 12, 13),
                end_date=date(2025, 12, 16),
                definite_date=date(2025, 12, 15),
                attendance_type="Open for all",
                visibility="Open",
                # details
                budget=500.0,
                description="Weekend food tour in Barcelona",
                restaurant_name="Cal Pep",
                picture="/static/images/barcelona-food-place.jpeg",
                trip_preferences="Seafood, Local cuisine",
                # capacity
                max_participants=4,
                is_open=True,
                is_cancelled=False,
                trip_type="Brunch",
                trip_state="active",
            )

            trip2 = Trip(
                title="Valencia Paella Experience",
                creator_id=user2.id,
                destination_city_id=valencia.id,
                possible_cities="Valencia",
                start_date=date(2025, 11, 19),
                end_date=date(2025, 11, 21),
                definite_date=date(2025, 11, 20),
                attendance_type="Open for all",
                visibility="Open",
                budget=300.0,
                description="Paella cooking class adventure",
                restaurant_name=None,
                picture=None,
                trip_preferences="Traditional Spanish, Cooking classes",
                max_participants=6,
                is_open=True,
                is_cancelled=False,
                trip_type="lunch",
                trip_state="active",
            )

            trip3 = Trip(
                title="Seville Tapas Tour",
                creator_id=user3.id,
                destination_city_id=seville.id,
                possible_cities="Seville, Cordoba, Granada",
                start_date=None,
                end_date=None,
                definite_date=None,  # Testing flexible dates
                attendance_type="Open for all",
                visibility="Open",
                budget=800.0,
                description="Tapas crawl through historic Seville",
                restaurant_name=None,
                picture=None,
                trip_preferences="Tapas, Wine bars, Local spots",
                max_participants=8,
                is_open=True,
                is_cancelled=False,
                trip_type="dinner",
                trip_state="planning",
            )

            db.session.add_all([trip1, trip2, trip3])
            db.session.commit()
            print(f"✅ Created {Trip.query.count()} trips")

            # 7. Create Trip Participants
            print("🎫 Creating trip participants...")
            participant1 = Trip_participants(
                trip_id=trip1.id, user_id=user2.id, editing_permissions=False
            )
            participant2 = Trip_participants(
                trip_id=trip1.id, user_id=user3.id, editing_permissions=True
            )
            participant3 = Trip_participants(
                trip_id=trip2.id, user_id=user1.id, editing_permissions=False
            )
            participant4 = Trip_participants(
                trip_id=trip3.id, user_id=user4.id, editing_permissions=True
            )

            db.session.add_all(
                [participant1, participant2, participant3, participant4]
            )
            db.session.commit()
            print(f"✅ Created {Trip_participants.query.count()} trip participants")

            # 8. Create Trip Invitations (new table)
            print("✉️ Creating trip invitations...")
            # trip1: bob and carol invited
            invite1 = Trip_invitations(trip_id=trip1.id, user_id=user2.id)
            invite2 = Trip_invitations(trip_id=trip1.id, user_id=user3.id)
            # trip2: alice invited
            invite3 = Trip_invitations(trip_id=trip2.id, user_id=user1.id)
            # trip3: david invited
            invite4 = Trip_invitations(trip_id=trip3.id, user_id=user4.id)

            db.session.add_all([invite1, invite2, invite3, invite4])
            db.session.commit()
            print(f"✅ Created {Trip_invitations.query.count()} trip invitations")

            # 9. Create Meetups (matching Meetups model)
            print("📅 Creating meetups...")
            meetup1 = Meetups(
                trip_id=trip1.id,
                user_id=user1.id,
                content="Pre-trip planning dinner",
                location="Café Central",
                city_id=madrid.id,
                date=date(2025, 12, 10),
                time=time(19, 30),
                status="PLANNING",
            )

            meetup2 = Meetups(
                trip_id=trip2.id,
                user_id=user2.id,
                content="Market visit before cooking class",
                location="Mercado Central",
                city_id=valencia.id,
                date=date(2025, 11, 20),
                time=time(10, 0),
                status="PLANNING",
            )

            meetup3 = Meetups(
                trip_id=trip1.id,
                user_id=user3.id,
                content="Airport meetup",
                location="Barcelona Airport T1",
                city_id=barcelona.id,
                date=date(2025, 12, 15),
                time=time(14, 0),
                status="PLANNING",
            )

            db.session.add_all([meetup1, meetup2, meetup3])
            db.session.commit()
            print(f"✅ Created {Meetups.query.count()} meetups")

            # 10. Create Trip Comments (matching TripComment model)
            print("💬 Creating trip comments...")
            comment1 = TripComment(
                trip_id=trip1.id,
                author_id=user2.id,
                content="This sounds amazing! I'm definitely interested in joining.",
            )

            comment2 = TripComment(
                trip_id=trip1.id,
                author_id=user3.id,
                content=(
                    "I know some great local spots in Barcelona. "
                    "Let me share some recommendations!"
                ),
            )

            comment3 = TripComment(
                trip_id=trip2.id,
                author_id=user1.id,
                content=(
                    "I've always wanted to learn how to make authentic paella. "
                    "Count me in!"
                ),
            )

            comment4 = TripComment(
                trip_id=trip3.id,
                author_id=user4.id,
                content=(
                    "Seville has the best tapas in Spain. I can be your local guide!"
                ),
            )

            db.session.add_all([comment1, comment2, comment3, comment4])
            db.session.commit()
            print(f"✅ Created {TripComment.query.count()} trip comments")

            # 11. Create Trip Stops (matching TripStop model)
            print("🛑 Creating trip stops...")
            stop1 = TripStop(
                trip_id=trip1.id,
                name="Lunch at Cal Pep",
                place="Cal Pep",
                date=date(2025, 12, 15),
                time=time(13, 0),
                address="Plaça de les Olles, 8, Barcelona",
                budget_per_person=35.0,
                notes="Famous for seafood tapas. Arrive early!",
                status="Just Ideas",
                order=1,
            )

            stop2 = TripStop(
                trip_id=trip1.id,
                name="Coffee at Satan's Coffee Corner",
                place="Satan's Coffee Corner",
                date=date(2025, 12, 15),
                time=time(10, 30),
                address="Carrer de l'Arc de Sant Ramon del Call, 11, Barcelona",
                budget_per_person=5.0,
                notes="Best coffee in the Gothic Quarter",
                status="Rough Draft",
                order=0,
            )

            stop3 = TripStop(
                trip_id=trip2.id,
                name="Paella cooking class",
                place="Valencia Cooking School",
                date=date(2025, 11, 20),
                time=time(11, 0),
                address="Carrer de la Pau, 25, Valencia",
                budget_per_person=85.0,
                notes="Includes market tour and lunch",
                status="Final Plan",
                order=1,
            )

            stop4 = TripStop(
                trip_id=trip3.id,
                name="Tapas at Bar El Comercio",
                place="Bar El Comercio",
                date=None,
                time=None,
                address="Calle Lineros, Seville",
                budget_per_person=20.0,
                notes="Traditional tapas bar, cash only",
                status="Just Ideas",
                order=0,
            )

            db.session.add_all([stop1, stop2, stop3, stop4])
            db.session.commit()
            print(f"✅ Created {TripStop.query.count()} trip stops")

            print("\n🎉 Test data creation completed successfully!")

            # Verification queries
            print("\n📊 Database Summary:")
            print(f"   • Users: {User.query.count()}")
            print(f"   • Cities: {City.query.count()}")
            print(f"   • Neighborhoods: {Neighborhood.query.count()}")
            print(f"   • Trips: {Trip.query.count()}")
            print(f"   • Trip stops: {TripStop.query.count()}")
            print(f"   • Interests: {Interest.query.count()}")
            print(f"   • Following relationships: {FollowingAssociation.query.count()}")
            print(f"   • Trip participants: {Trip_participants.query.count()}")
            print(f"   • Trip invitations: {Trip_invitations.query.count()}")
            print(f"   • Meetups: {Meetups.query.count()}")
            print(f"   • Trip comments: {TripComment.query.count()}")

            # Test some relationships
            print("\n🔗 Testing Relationships:")
            alice = User.query.filter_by(name="Alice Johnson").first()
            if alice:
                print(f"   • Alice's interests: {[i.interest for i in alice.interests]}")
                print(f"   • Alice's city: {alice.city.name if alice.city else 'None'}")
                print(f"   • Alice's trips created: {len(alice.trips_created)}")
                print(
                    f"   • Alice's trip invitations: "
                    f"{[(inv.trip.title) for inv in alice.trip_invitations]}"
                )

            barcelona_trip = Trip.query.filter_by(
                description="Weekend food tour in Barcelona"
            ).first()
            if barcelona_trip:
                print(
                    f"   • Barcelona trip participants: "
                    f"{len(barcelona_trip.participants)}"
                )
                print(
                    f"   • Barcelona trip meetups: {len(barcelona_trip.meetups)}"
                )
                print(
                    f"   • Barcelona trip invitations: "
                    f"{len(barcelona_trip.invitations)}"
                )
                print(
                    f"   • Barcelona trip stops: {len(barcelona_trip.stops)}"
                )

        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.session.rollback()
            raise e


def clear_test_data():
    """Clear all test data from the database"""
    app = create_app()
    with app.app_context():
        print("🧹 Clearing all test data...")

        # Delete in reverse order of dependencies
        TripComment.query.delete()
        Meetups.query.delete()
        TripStop.query.delete()
        Trip_participants.query.delete()
        Trip_invitations.query.delete()
        Trip.query.delete()
        FollowingAssociation.query.delete()
        Interest.query.delete()
        User.query.delete()
        Neighborhood.query.delete()
        City.query.delete()

        db.session.commit()
        print("✅ All test data cleared!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_test_data()
    else:
        create_test_data()