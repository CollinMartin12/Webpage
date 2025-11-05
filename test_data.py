#!/usr/bin/env python3
"""
Test Data Script for Microblog Application
==========================================
This script inserts test data into all tables to verify the database schema is working correctly.
Run this script after your database is initialized.

Usage:
  python test_data.py
"""

from microblog import create_app
from microblog.model import db, User, City, Neighborhood, RestaurantType, TripType, Trip, Interest, FollowingAssociation, Trip_participants, Meetups, TripComment
import datetime
from datetime import date, time

def create_test_data():
    app = create_app()
    with app.app_context():
        print("🧪 Creating test data...")
        
        try:
            # 1. Create Cities
            print("📍 Creating cities...")
            madrid = City(name="Madrid")
            barcelona = City(name="Barcelona")
            valencia = City(name="Valencia")
            seville = City(name="Seville")
            bilbao = City(name="Bilbao")
            
            db.session.add_all([madrid, barcelona, valencia, seville, bilbao])
            db.session.commit()
            print(f"✅ Created {City.query.count()} cities")

            # 2. Create Neighborhoods
            print("🏘️ Creating neighborhoods...")
            centro = Neighborhood(name="Centro")
            malasana = Neighborhood(name="Malasaña")
            chueca = Neighborhood(name="Chueca")
            gracia = Neighborhood(name="Gràcia")
            eixample = Neighborhood(name="Eixample")
            ciutat_vella = Neighborhood(name="Ciutat Vella")
            
            db.session.add_all([centro, malasana, chueca, gracia, eixample, ciutat_vella])
            db.session.commit()
            print(f"✅ Created {Neighborhood.query.count()} neighborhoods")

            # 3. Create Restaurant Types
            print("🍽️ Creating restaurant types...")
            italian = RestaurantType(name="Italian")
            spanish = RestaurantType(name="Spanish")
            chinese = RestaurantType(name="Chinese")
            american = RestaurantType(name="American")
            mexican = RestaurantType(name="Mexican")
            japanese = RestaurantType(name="Japanese")
            
            db.session.add_all([italian, spanish, chinese, american, mexican, japanese])
            db.session.commit()
            print(f"✅ Created {RestaurantType.query.count()} restaurant types")

            # 4. Create Trip Types
            print("🍳 Creating trip types...")
            breakfast = TripType(name="Breakfast")
            lunch = TripType(name="Lunch")
            dinner = TripType(name="Dinner")
            brunch = TripType(name="Brunch")
            
            db.session.add_all([breakfast, lunch, dinner, brunch])
            db.session.commit()
            print(f"✅ Created {TripType.query.count()} trip types")

            # 5. Create Users
            print("👥 Creating users...")
            user1 = User(
                email="alice@example.com",
                name="Alice Johnson",
                password="hashed_password_123",
                description="Food lover from Madrid",
                city_id=madrid.id,
                neighborhood_id=centro.id
            )
            
            user2 = User(
                email="bob@example.com",
                name="Bob Martinez",
                password="hashed_password_456",
                description="Chef exploring Spanish cuisine",
                city_id=barcelona.id,
                neighborhood_id=gracia.id
            )
            
            user3 = User(
                email="carol@example.com",
                name="Carol Smith",
                password="hashed_password_789",
                description="Travel blogger and foodie",
                city_id=valencia.id,
                neighborhood_id=None  # Testing nullable neighborhood
            )
            
            user4 = User(
                email="david@example.com",
                name="David Rodriguez",
                password="hashed_password_101",
                description="Local food guide",
                city_id=None,  # Testing nullable city
                neighborhood_id=None
            )
            
            db.session.add_all([user1, user2, user3, user4])
            db.session.commit()
            print(f"✅ Created {User.query.count()} users")

            # 6. Create Interests
            print("💭 Creating interests...")
            interest1 = Interest(user_id=user1.id, interest="Italian cuisine")
            interest2 = Interest(user_id=user1.id, interest="Wine tasting")
            interest3 = Interest(user_id=user2.id, interest="Street food")
            interest4 = Interest(user_id=user3.id, interest="Vegetarian food")
            interest5 = Interest(user_id=user4.id, interest="Michelin starred restaurants")
            
            db.session.add_all([interest1, interest2, interest3, interest4, interest5])
            db.session.commit()
            print(f"✅ Created {Interest.query.count()} interests")

            # 7. Create Following relationships
            print("👤 Creating following relationships...")
            follow1 = FollowingAssociation(follower_id=user1.id, followed_id=user2.id)
            follow2 = FollowingAssociation(follower_id=user1.id, followed_id=user3.id)
            follow3 = FollowingAssociation(follower_id=user2.id, followed_id=user1.id)
            follow4 = FollowingAssociation(follower_id=user3.id, followed_id=user4.id)
            
            db.session.add_all([follow1, follow2, follow3, follow4])
            db.session.commit()
            print(f"✅ Created {FollowingAssociation.query.count()} following relationships")

            # 8. Create Trips
            print("✈️ Creating trips...")
            trip1 = Trip(
                creator_id=user1.id,
                departure_city_id=madrid.id,
                departure_neighborhood_id=centro.id,
                destination_city_id=barcelona.id,
                destination_neighborhood_id=gracia.id,
                definite_date=date(2025, 12, 15),
                status="Planning",
                budget=500.0,
                description="Weekend food tour in Barcelona",
                restaurant_name="Cal Pep",
                trip_type_id=dinner.id,
                max_participants=4,
                is_open=True,
                picture="/static/images/Barcelona Food Place.jpeg"
            )

            trip2 = Trip(
                creator_id=user2.id,
                departure_city_id=barcelona.id,
                destination_city_id=valencia.id,
                definite_date=date(2025, 11, 20),
                status="Planning",
                budget=300.0,
                description="Paella cooking class adventure",
                trip_type_id=lunch.id,
                max_participants=6,
                is_open=True
            )
            
            trip3 = Trip(
                creator_id=user3.id,
                destination_city_id=seville.id,
                definite_date=None,  # Testing flexible dates
                status="Planning",
                budget=800.0,
                description="Tapas crawl through historic Seville",
                trip_type_id=dinner.id,
                max_participants=8,
                is_open=True
            )
            
            db.session.add_all([trip1, trip2, trip3])
            db.session.commit()
            print(f"✅ Created {Trip.query.count()} trips")

            # 9. Add restaurant types to trips (many-to-many)
            print("🍴 Adding restaurant types to trips...")
            trip1.restaurant_types.extend([spanish, italian])
            trip2.restaurant_types.append(spanish)
            trip3.restaurant_types.extend([spanish, american])
            db.session.commit()
            print("✅ Added restaurant types to trips")

            # 10. Create Trip Participants
            print("🎫 Creating trip participants...")
            participant1 = Trip_participants(trip_id=trip1.id, user_id=user2.id, editing_permissions=False)
            participant2 = Trip_participants(trip_id=trip1.id, user_id=user3.id, editing_permissions=True)
            participant3 = Trip_participants(trip_id=trip2.id, user_id=user1.id, editing_permissions=False)
            participant4 = Trip_participants(trip_id=trip3.id, user_id=user4.id, editing_permissions=True)
            
            db.session.add_all([participant1, participant2, participant3, participant4])
            db.session.commit()
            print(f"✅ Created {Trip_participants.query.count()} trip participants")

            # 11. Create Meetups
            print("📅 Creating meetups...")
            meetup1 = Meetups(
                trip_id=trip1.id,
                user_id=user1.id,
                content="Pre-trip planning dinner",
                location="Café Central",
                city_id=madrid.id,
                date=date(2025, 12, 10),
                time=time(19, 30),
                status="PLANNING"
            )
            
            meetup2 = Meetups(
                trip_id=trip2.id,
                user_id=user2.id,
                content="Market visit before cooking class",
                location="Mercado Central",
                city_id=valencia.id,
                date=date(2025, 11, 20),
                time=time(10, 0),
                status="PLANNING"
            )
            
            meetup3 = Meetups(
                trip_id=trip1.id,
                user_id=user3.id,
                content="Airport meetup",
                location="Barcelona Airport T1",
                city_id=barcelona.id,
                date=date(2025, 12, 15),
                time=time(14, 0),
                status="PLANNING"
            )
            
            db.session.add_all([meetup1, meetup2, meetup3])
            db.session.commit()
            print(f"✅ Created {Meetups.query.count()} meetups")

            # 12. Create Trip Comments
            print("💬 Creating trip comments...")
            comment1 = TripComment(
                trip_id=trip1.id,
                author_id=user2.id,
                content="This sounds amazing! I'm definitely interested in joining."
            )
            
            comment2 = TripComment(
                trip_id=trip1.id,
                author_id=user3.id,
                content="I know some great local spots in Barcelona. Let me share some recommendations!"
            )
            
            comment3 = TripComment(
                trip_id=trip2.id,
                author_id=user1.id,
                content="I've always wanted to learn how to make authentic paella. Count me in!"
            )
            
            comment4 = TripComment(
                trip_id=trip3.id,
                author_id=user4.id,
                content="Seville has the best tapas in Spain. I can be your local guide!"
            )
            
            db.session.add_all([comment1, comment2, comment3, comment4])
            db.session.commit()
            print(f"✅ Created {TripComment.query.count()} trip comments")

            print("\n🎉 Test data creation completed successfully!")
            
            # Verification queries
            print("\n📊 Database Summary:")
            print(f"   • Users: {User.query.count()}")
            print(f"   • Cities: {City.query.count()}")
            print(f"   • Neighborhoods: {Neighborhood.query.count()}")
            print(f"   • Restaurant Types: {RestaurantType.query.count()}")
            print(f"   • Trip Types: {TripType.query.count()}")
            print(f"   • Trips: {Trip.query.count()}")
            print(f"   • Interests: {Interest.query.count()}")
            print(f"   • Following relationships: {FollowingAssociation.query.count()}")
            print(f"   • Trip participants: {Trip_participants.query.count()}")
            print(f"   • Meetups: {Meetups.query.count()}")
            print(f"   • Trip comments: {TripComment.query.count()}")
            
            # Test some relationships
            print("\n🔗 Testing Relationships:")
            alice = User.query.filter_by(name="Alice Johnson").first()
            print(f"   • Alice's interests: {[i.interest for i in alice.interests]}")
            print(f"   • Alice's city: {alice.city.name if alice.city else 'None'}")
            print(f"   • Alice's trips created: {len(alice.trips_created)}")
            
            barcelona_trip = Trip.query.filter_by(description="Weekend food tour in Barcelona").first()
            print(f"   • Barcelona trip participants: {len(barcelona_trip.participants)}")
            print(f"   • Barcelona trip restaurant types: {[rt.name for rt in barcelona_trip.restaurant_types]}")
            print(f"   • Barcelona trip meetups: {len(barcelona_trip.meetups)}")

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
        Trip_participants.query.delete()
        # Clear many-to-many relationships
        for trip in Trip.query.all():
            trip.restaurant_types.clear()
        Trip.query.delete()
        FollowingAssociation.query.delete()
        Interest.query.delete()
        User.query.delete()
        TripType.query.delete()
        RestaurantType.query.delete()
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
