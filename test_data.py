#!/usr/bin/env python3
"""
Comprehensive Test Data Script for Trip Planning Application
=============================================================
This script creates a rich, realistic dataset with extensive test data
for users, trips, stops, meetups, comments, and relationships.

Usage:
  python test_data.py              # Create test data
  python test_data.py clear        # Clear all test data
  python test_data.py stats        # Show database statistics
"""

from datetime import date, time, datetime, timedelta
import random

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
    TripImage,
)


PROFILE_PHOTOS =[
    "https://plus.unsplash.com/premium_vector-1682269284255-8209b981c625?q=80&w=2960&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://plus.unsplash.com/premium_vector-1682269287900-d96e9a6c188b?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://plus.unsplash.com/premium_vector-1682269282372-6d888f3451f1?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://images.unsplash.com/vector-1740737650825-1ce4f5377085?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
]
# Rich test data definitions
CITIES_DATA = [
    "Madrid", "Barcelona", "Valencia", "Seville", "Bilbao",
    "Granada", "Málaga", "Zaragoza", "Alicante", "Córdoba",
    "Murcia", "San Sebastián", "Salamanca", "Toledo", "Santander"
]

NEIGHBORHOODS_DATA = {
    "Madrid": ["Centro", "Malasaña", "Chueca", "Retiro", "Salamanca", "Chamberí"],
    "Barcelona": ["Gràcia", "Eixample", "Ciutat Vella", "Born", "Raval", "Gótico"],
    "Valencia": ["Ciutat Vella", "Ruzafa", "El Carmen", "Benimaclet", "Campanar"],
    "Seville": ["Triana", "Alameda", "Nervión", "Macarena", "Santa Cruz"],
    "San Sebastián": ["Parte Vieja", "Gros", "Centro", "Amara"]
}

USERS_DATA = [
    {
        "email": "elena.garcia@example.com",
        "name": "Elena García",
        "description": "Food photographer passionate about traditional Spanish cuisine. Love discovering hidden gems!",
        "city": "Madrid",
        "neighborhood": "Malasaña",
        "interests": ["Food Photography", "Traditional Tapas", "Wine Pairing", "Culinary History"]
    },
    {
        "email": "marcos.silva@example.com",
        "name": "Marcos Silva",
        "description": "Chef and restaurant consultant. Always on the hunt for the next Michelin star experience.",
        "city": "Barcelona",
        "neighborhood": "Eixample",
        "interests": ["Fine Dining", "Molecular Gastronomy", "Catalan Cuisine", "Chef Networking"]
    },
    {
        "email": "sofia.rodriguez@example.com",
        "name": "Sofía Rodríguez",
        "description": "Travel blogger writing about sustainable food tourism. Vegetarian exploring Spain.",
        "city": "Valencia",
        "neighborhood": "Ruzafa",
        "interests": ["Vegetarian Cuisine", "Farm-to-Table", "Sustainable Tourism", "Food Blogging"]
    },
    {
        "email": "diego.martin@example.com",
        "name": "Diego Martín",
        "description": "Local food tour guide in Seville. Expert on Andalusian tapas culture and sherry.",
        "city": "Seville",
        "neighborhood": "Triana",
        "interests": ["Tapas Culture", "Sherry Tasting", "Local History", "Andalusian Cuisine"]
    },
    {
        "email": "lucia.torres@example.com",
        "name": "Lucía Torres",
        "description": "Wine sommelier and educator. Organizing wine tours across Spanish wine regions.",
        "city": "Barcelona",
        "neighborhood": "Gràcia",
        "interests": ["Wine Education", "Rioja Region", "Wine Tours", "Spanish Varietals"]
    },
    {
        "email": "javier.lopez@example.com",
        "name": "Javier López",
        "description": "Pintxos enthusiast from San Sebastián. Former chef, now food culture researcher.",
        "city": "San Sebastián",
        "neighborhood": "Parte Vieja",
        "interests": ["Pintxos", "Basque Cuisine", "Gastronomy Research", "Cider Houses"]
    },
    {
        "email": "carmen.hernandez@example.com",
        "name": "Carmen Hernández",
        "description": "University student studying nutrition. Love brunch spots and healthy Mediterranean food.",
        "city": "Madrid",
        "neighborhood": "Chueca",
        "interests": ["Healthy Eating", "Brunch Culture", "Mediterranean Diet", "Food Science"]
    },
    {
        "email": "pablo.sanchez@example.com",
        "name": "Pablo Sánchez",
        "description": "Street food lover and market explorer. Always looking for authentic local experiences.",
        "city": "Valencia",
        "neighborhood": "El Carmen",
        "interests": ["Street Food", "Local Markets", "Food History", "Budget Travel"]
    },
    {
        "email": "andrea.moreno@example.com",
        "name": "Andrea Moreno",
        "description": "Pastry chef specializing in traditional Spanish desserts. Sweet tooth always active!",
        "city": "Barcelona",
        "neighborhood": "Born",
        "interests": ["Pastry Arts", "Traditional Desserts", "Chocolate", "Bakery Culture"]
    },
    {
        "email": "fernando.ruiz@example.com",
        "name": "Fernando Ruiz",
        "description": "Food journalist covering restaurant openings and culinary trends in Spain.",
        "city": "Madrid",
        "neighborhood": "Salamanca",
        "interests": ["Food Journalism", "Restaurant Reviews", "Culinary Trends", "Chef Interviews"]
    },
    {
        "email": "isabel.jimenez@example.com",
        "name": "Isabel Jiménez",
        "description": "Expat from Mexico exploring Spanish-Latin fusion. Cooking instructor on weekends.",
        "city": "Seville",
        "neighborhood": "Alameda",
        "interests": ["Fusion Cuisine", "Mexican Food", "Cooking Classes", "Cultural Exchange"]
    },
    {
        "email": "ramon.gil@example.com",
        "name": "Ramón Gil",
        "description": "Seafood fanatic living near the coast. Marine biologist who loves coastal gastronomy.",
        "city": "San Sebastián",
        "neighborhood": "Gros",
        "interests": ["Seafood", "Coastal Cuisine", "Sustainable Fishing", "Marine Biology"]
    },
    {
        "email": "natalia.castro@example.com",
        "name": "Natalia Castro",
        "description": "Organic food advocate and farmers market organizer. Passionate about local produce.",
        "city": "Valencia",
        "neighborhood": "Benimaclet",
        "interests": ["Organic Food", "Farmers Markets", "Seasonal Cooking", "Zero Waste"]
    },
    {
        "email": "miguel.ortiz@example.com",
        "name": "Miguel Ortiz",
        "description": "Beer enthusiast exploring craft breweries. Also love pairing beer with traditional food.",
        "city": "Madrid",
        "neighborhood": "Centro",
        "interests": ["Craft Beer", "Beer Pairing", "Brewery Tours", "Pub Culture"]
    },
    {
        "email": "laura.navarro@example.com",
        "name": "Laura Navarro",
        "description": "Culinary student documenting my journey through Spanish regional cuisines.",
        "city": "Barcelona",
        "neighborhood": "Raval",
        "interests": ["Culinary School", "Regional Cuisine", "Recipe Development", "Food Styling"]
    }
]

TRIPS_DATA = [
    {
        "title": "Ultimate Tapas Crawl - Old Madrid",
        "description": "Authentic tapas experience through historic Madrid neighborhoods, visiting 6-7 classic tabernas",
        "destination_city": "Madrid",
        "possible_cities": "Madrid",
        "start_date": date.today() + timedelta(days=15),
        "end_date": date.today() + timedelta(days=15),
        "budget": 45.0,
        "restaurant_name": "Casa Lucio",
        "trip_type": "dinner",
        "trip_preferences": "Traditional Spanish, Local atmosphere, No tourists",
        "max_participants": 8,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "Valencia Paella Master Class",
        "description": "Learn to cook authentic Valencian paella with a local chef, including market tour and wine pairing",
        "destination_city": "Valencia",
        "possible_cities": "Valencia, Albufera",
        "start_date": date.today() + timedelta(days=22),
        "end_date": date.today() + timedelta(days=22),
        "budget": 95.0,
        "restaurant_name": "La Pepica",
        "trip_type": "lunch",
        "trip_preferences": "Traditional paella, Rice dishes, Local wine",
        "max_participants": 12,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "San Sebastián Pintxos Marathon",
        "description": "Epic pintxos tour through the Parte Vieja, hitting the best bars with a local guide",
        "destination_city": "San Sebastián",
        "possible_cities": "San Sebastián",
        "start_date": date.today() + timedelta(days=30),
        "end_date": date.today() + timedelta(days=31),
        "budget": 75.0,
        "restaurant_name": "La Cuchara de San Telmo",
        "trip_type": "dinner",
        "trip_preferences": "Pintxos, Basque cuisine, Txakoli wine",
        "max_participants": 10,
        "is_open": True,
        "attendance_type": "With Specific People",
        "visibility": "Friends-Only",
        "trip_state": "Final Plan"
    },
    {
        "title": "Barcelona Brunch Club - Gothic Quarter",
        "description": "Exploring the best brunch spots in the Gothic Quarter and Born neighborhoods",
        "destination_city": "Barcelona",
        "possible_cities": "Barcelona",
        "start_date": date.today() + timedelta(days=8),
        "end_date": date.today() + timedelta(days=8),
        "budget": 28.0,
        "trip_type": "Brunch",
        "trip_preferences": "Specialty coffee, Avocado toast, Artisanal bakeries",
        "max_participants": 6,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Rough Draft"
    },
    {
        "title": "Michelin Star Tasting Experience - Basque Country",
        "description": "Three-day culinary journey visiting Michelin-starred restaurants in San Sebastián and Bilbao",
        "destination_city": "San Sebastián",
        "possible_cities": "San Sebastián, Bilbao, Getaria",
        "start_date": date.today() + timedelta(days=45),
        "end_date": date.today() + timedelta(days=47),
        "budget": 450.0,
        "restaurant_name": "Arzak",
        "trip_type": "dinner",
        "trip_preferences": "Fine dining, Tasting menus, Wine pairing, Modern Basque",
        "max_participants": 4,
        "is_open": True,
        "attendance_type": "With Specific People",
        "visibility": "Friends-Only",
        "trip_state": "Final Plan"
    },
    {
        "title": "Seville Flamenco & Food Night",
        "description": "Traditional Andalusian dinner followed by authentic flamenco show in Triana",
        "destination_city": "Seville",
        "possible_cities": "Seville",
        "start_date": date.today() + timedelta(days=18),
        "end_date": date.today() + timedelta(days=18),
        "budget": 65.0,
        "restaurant_name": "Abantal",
        "trip_type": "dinner",
        "trip_preferences": "Andalusian cuisine, Flamenco culture, Sherry wine",
        "max_participants": 12,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "Wine & Cheese Pairing Workshop",
        "description": "Intimate workshop exploring Spanish cheeses with perfect wine pairings, led by a sommelier",
        "destination_city": "Madrid",
        "possible_cities": "Madrid",
        "start_date": date.today() + timedelta(days=12),
        "end_date": date.today() + timedelta(days=12),
        "budget": 55.0,
        "trip_type": "Brunch",
        "trip_preferences": "Wine education, Artisan cheese, Small groups",
        "max_participants": 8,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "Valencia Market to Table Experience",
        "description": "Morning at Mercado Central followed by cooking fresh ingredients at a local chef's home",
        "destination_city": "Valencia",
        "possible_cities": "Valencia",
        "start_date": date.today() + timedelta(days=25),
        "end_date": date.today() + timedelta(days=25),
        "budget": 70.0,
        "restaurant_name": "Central Market",
        "trip_type": "lunch",
        "trip_preferences": "Fresh produce, Home cooking, Sustainable food",
        "max_participants": 6,
        "is_open": True,
        "attendance_type": "With Specific People",
        "visibility": "Friends-Only",
        "trip_state": "Rough Draft"
    },
    {
        "title": "Barcelona Chocolate & Pastry Tour",
        "description": "Sweet afternoon exploring historic chocolate shops and modern patisseries in Barcelona",
        "destination_city": "Barcelona",
        "possible_cities": "Barcelona",
        "start_date": date.today() + timedelta(days=10),
        "end_date": date.today() + timedelta(days=10),
        "budget": 35.0,
        "trip_type": "Brunch",
        "trip_preferences": "Desserts, Chocolate, Pastries, Coffee",
        "max_participants": 10,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "Seafood Extravaganza - Galician Coast",
        "description": "Fresh seafood feast exploring coastal restaurants and fishing villages near Santander",
        "destination_city": "Santander",
        "possible_cities": "Santander, Castro Urdiales",
        "start_date": date.today() + timedelta(days=35),
        "end_date": date.today() + timedelta(days=36),
        "budget": 85.0,
        "trip_type": "lunch",
        "trip_preferences": "Fresh fish, Shellfish, Coastal views, Albariño wine",
        "max_participants": 8,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Just Ideas"
    },
    {
        "title": "Madrid Street Food Festival",
        "description": "Exploring food trucks and street vendors at the monthly Madrid food market",
        "destination_city": "Madrid",
        "possible_cities": "Madrid",
        "start_date": date.today() + timedelta(days=5),
        "end_date": date.today() + timedelta(days=5),
        "budget": 25.0,
        "trip_type": "lunch",
        "trip_preferences": "Street food, International fusion, Budget-friendly",
        "max_participants": 15,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "Traditional Andalusian Breakfast Tour",
        "description": "Morning tour of Seville's best breakfast spots featuring churros, tostadas, and coffee",
        "destination_city": "Seville",
        "possible_cities": "Seville",
        "start_date": date.today() + timedelta(days=14),
        "end_date": date.today() + timedelta(days=14),
        "budget": 18.0,
        "trip_type": "Breakfast",
        "trip_preferences": "Traditional breakfast, Coffee culture, Local bakeries",
        "max_participants": 8,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "Vegan Tapas Innovation Night",
        "description": "Discovering Barcelona's innovative vegan tapas scene in Raval and Gràcia",
        "destination_city": "Barcelona",
        "possible_cities": "Barcelona",
        "start_date": date.today() + timedelta(days=20),
        "end_date": date.today() + timedelta(days=20),
        "budget": 40.0,
        "trip_type": "dinner",
        "trip_preferences": "Vegan, Plant-based, Innovative cuisine, Sustainable",
        "max_participants": 6,
        "is_open": True,
        "attendance_type": "With Specific People",
        "visibility": "Friends-Only",
        "trip_state": "Rough Draft"
    },
    {
        "title": "Craft Beer & Pintxos Pairing",
        "description": "Exploring Madrid's craft beer scene with perfect pintxos pairings at each stop",
        "destination_city": "Madrid",
        "possible_cities": "Madrid",
        "start_date": date.today() + timedelta(days=28),
        "end_date": date.today() + timedelta(days=28),
        "budget": 42.0,
        "trip_type": "dinner",
        "trip_preferences": "Craft beer, Beer pairing, Casual atmosphere",
        "max_participants": 10,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Final Plan"
    },
    {
        "title": "Cordoba Culinary Heritage Tour",
        "description": "Day trip exploring Cordoba's Jewish quarter with traditional Sephardic and Moorish cuisine",
        "destination_city": "Córdoba",
        "possible_cities": "Córdoba",
        "start_date": date.today() + timedelta(days=40),
        "end_date": date.today() + timedelta(days=40),
        "budget": 60.0,
        "trip_type": "lunch",
        "trip_preferences": "Historical cuisine, Cultural heritage, Walking tour",
        "max_participants": 12,
        "is_open": True,
        "attendance_type": "Open for all",
        "visibility": "Open",
        "trip_state": "Just Ideas"
    }
]


def create_test_data():
    """Create comprehensive test data for the trip planning application"""
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("🚀 COMPREHENSIVE TEST DATA CREATION")
        print("=" * 70)
        
        # Clear existing data first
        print("\n🧹 Clearing existing data...")
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
            print("   ✅ Cleared existing data")
        except Exception as e:
            print(f"   ⚠️  Note: {e}")
            db.session.rollback()

        try:
            # 1. Create Cities
            print("\n📍 Creating cities...")
            cities = {}
            for city_name in CITIES_DATA:
                city = City(name=city_name)
                db.session.add(city)
                db.session.flush()
                cities[city_name] = city
                print(f"   ✓ {city_name}")
            db.session.commit()
            print(f"   ✅ Created {len(cities)} cities")


            # 2. Create Neighborhoods
            print("\n🏘️  Creating neighborhoods...")
            neighborhoods = {}
            neighborhood_count = 0
            for city_name, neighborhood_list in NEIGHBORHOODS_DATA.items():
                for neighborhood_name in neighborhood_list:
                    neighborhood = Neighborhood(name=neighborhood_name)
                    db.session.add(neighborhood)
                    db.session.flush()
                    neighborhoods[f"{city_name}-{neighborhood_name}"] = neighborhood
                    neighborhood_count += 1
                    print(f"   ✓ {neighborhood_name} ({city_name})")
            db.session.commit()
            print(f"   ✅ Created {neighborhood_count} neighborhoods")

            # 3. Create Users
            print("\n👥 Creating users...")
            users = []
            for user_data in USERS_DATA:
                city = cities.get(user_data["city"])
                neighborhood_key = f"{user_data['city']}-{user_data.get('neighborhood', '')}"
                neighborhood = neighborhoods.get(neighborhood_key)
                
                user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    password="hashed_password_" + user_data["name"].replace(" ", "_").lower(),
                    description=user_data["description"],
                    city_id=city.id if city else None,
                    neighborhood_id=neighborhood.id if neighborhood else None,
                    profile_picture=random.choice(PROFILE_PHOTOS)
                )
                db.session.add(user)
                db.session.flush()
                users.append(user)
                print(f"   ✓ {user_data['name']} ({user_data['city']})")
            db.session.commit()
            print(f"   ✅ Created {len(users)} users")

            # 4. Create Interests
            print("\n💭 Creating interests...")
            interest_count = 0
            for i, user_data in enumerate(USERS_DATA):
                user = users[i]
                for interest_text in user_data.get("interests", []):
                    interest = Interest(user_id=user.id, interest=interest_text)
                    db.session.add(interest)
                    interest_count += 1
            db.session.commit()
            print(f"   ✅ Created {interest_count} interests")

            # 5. Create Following Relationships
            print("\n👤 Creating following relationships...")
            follows = []
            for i, user in enumerate(users):
                # Each user follows 3-7 random other users
                num_follows = random.randint(3, 7)
                potential_follows = [u for u in users if u.id != user.id]
                selected_follows = random.sample(potential_follows, min(num_follows, len(potential_follows)))
                
                for followed in selected_follows:
                    follow = FollowingAssociation(
                        follower_id=user.id,
                        followed_id=followed.id
                    )
                    db.session.add(follow)
                    follows.append(follow)
            db.session.commit()
            print(f"   ✅ Created {len(follows)} following relationships")

            # 6. Create Trips
            print("\n✈️  Creating trips...")
            trips = []
            for i, trip_data in enumerate(TRIPS_DATA):
                creator = users[i % len(users)]
                dest_city = cities.get(trip_data["destination_city"])
                
                trip = Trip(
                    title=trip_data["title"],
                    creator_id=creator.id,
                    destination_city_id=dest_city.id if dest_city else None,
                    possible_cities=trip_data.get("possible_cities"),
                    start_date=trip_data.get("start_date"),
                    end_date=trip_data.get("end_date"),
                    budget=trip_data.get("budget"),
                    description=trip_data["description"],
                    restaurant_name=trip_data.get("restaurant_name"),
                    picture=f"/static/images/trips/trip_{i+1}.jpg",
                    trip_type=trip_data.get("trip_type"),
                    trip_preferences=trip_data.get("trip_preferences"),
                    max_participants=trip_data.get("max_participants"),
                    is_open=trip_data.get("is_open", True),
                    attendance_type=trip_data.get("attendance_type", "Open for all"),
                    visibility=trip_data.get("visibility", "Open"),
                    trip_state=trip_data.get("trip_state", "Final Plan")
                )
                db.session.add(trip)
                db.session.flush()
                trips.append(trip)
                print(f"   ✓ {trip_data['title']}")
            db.session.commit()
            print(f"   ✅ Created {len(trips)} trips")

            # 7. Create Trip Participants
            print("\n👥 Creating trip participants...")
            participant_count = 0
            for trip in trips:
                # Creator is always a participant
                creator_participant = Trip_participants(
                    trip_id=trip.id,
                    user_id=trip.creator_id,
                    editing_permissions=True
                )
                db.session.add(creator_participant)
                participant_count += 1
                
                # Add 1-5 additional participants
                num_participants = random.randint(1, min(5, trip.max_participants - 1 if trip.max_participants else 5))
                potential_participants = [u for u in users if u.id != trip.creator_id]
                selected_participants = random.sample(potential_participants, min(num_participants, len(potential_participants)))
                
                for participant in selected_participants:
                    trip_participant = Trip_participants(
                        trip_id=trip.id,
                        user_id=participant.id,
                        editing_permissions=random.choice([True, False])
                    )
                    db.session.add(trip_participant)
                    participant_count += 1
            db.session.commit()
            print(f"   ✅ Created {participant_count} trip participants")

            # 8. Create Trip Invitations
            print("\n📨 Creating trip invitations...")
            invitation_count = 0
            for trip in trips:
                # Some trips have pending invitations
                if random.random() < 0.6:  # 60% of trips have invitations
                    num_invitations = random.randint(1, 3)
                    existing_participant_ids = [p.user_id for p in trip.participants]
                    potential_invitees = [u for u in users if u.id not in existing_participant_ids]
                    
                    if potential_invitees:
                        selected_invitees = random.sample(
                            potential_invitees, 
                            min(num_invitations, len(potential_invitees))
                        )
                        
                        for invitee in selected_invitees:
                            invitation = Trip_invitations(
                                trip_id=trip.id,
                                user_id=invitee.id,
                                invited_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                            )
                            db.session.add(invitation)
                            invitation_count += 1
            db.session.commit()
            print(f"   ✅ Created {invitation_count} trip invitations")

            # 9. Create Trip Stops
            print("\n🛑 Creating trip stops...")
            stop_templates = [
                {
                    "names": ["Breakfast at", "Morning coffee at", "Early bite at"],
                    "places": ["Local Café", "Artisan Bakery", "Coffee Shop", "Breakfast Bar"],
                    "budget_range": (5.0, 15.0),
                    "stop_type": "Breakfast",
                    "time_range": (time(8, 0), time(11, 0))
                },
                {
                    "names": ["Lunch at", "Midday meal at", "Afternoon dining at"],
                    "places": ["Tapas Bar", "Restaurant", "Bistro", "Market Hall"],
                    "budget_range": (15.0, 35.0),
                    "stop_type": "lunch",
                    "time_range": (time(13, 0), time(15, 30))
                },
                {
                    "names": ["Dinner at", "Evening meal at", "Sunset dining at"],
                    "places": ["Fine Restaurant", "Traditional Tavern", "Modern Eatery", "Rooftop Bar"],
                    "budget_range": (25.0, 75.0),
                    "stop_type": "dinner",
                    "time_range": (time(20, 0), time(22, 30))
                },
                {
                    "names": ["Coffee break at", "Dessert at", "Drinks at"],
                    "places": ["Café", "Pastry Shop", "Wine Bar", "Cocktail Lounge"],
                    "budget_range": (5.0, 20.0),
                    "stop_type": None,
                    "time_range": (time(16, 0), time(19, 0))
                }
            ]
            
            stop_count = 0
            for trip in trips:
                num_stops = num_stops = random.randint(0, 3)

                
                for order in range(num_stops):
                    template = random.choice(stop_templates)
                    stop_name_prefix = random.choice(template["names"])
                    stop_place = random.choice(template["places"])
                    
                    stop = TripStop(
                        trip_id=trip.id,
                        name=f"{stop_name_prefix} {stop_place}",
                        place=stop_place,
                        date=trip.start_date if trip.start_date else None,
                        time=time(
                            random.randint(template["time_range"][0].hour, template["time_range"][1].hour),
                            random.choice([0, 15, 30, 45])
                        ),
                        address=f"Calle Example {random.randint(1, 100)}, {trip.destination_city.name if trip.destination_city else 'Madrid'}",
                        budget_per_person=round(random.uniform(*template["budget_range"]), 2),
                        notes=random.choice([
                            "Reservation recommended",
                            "Walk-ins welcome",
                            "Cash only",
                            "Popular spot, arrive early",
                            "Great for groups",
                            "Vegetarian options available"
                        ]),
                        stop_type=template["stop_type"],
                        stop_status=random.choice(["Confirmed", "Tentative", "Considering"]),
                        order=order,
                        destination_type=random.choice(["Restaurant", "Café", "Bar", "Market"])
                    )
                    db.session.add(stop)
                    stop_count += 1
            db.session.commit()
            print(f"   ✅ Created {stop_count} trip stops")

            # 10. Create Meetups
            print("\n📍 Creating meetups...")
            meetup_count = 0
            for trip in trips:
                # 40% of trips have meetups
                if random.random() < 0.4:
                    num_meetups = random.randint(1, 2)
                    
                    for _ in range(num_meetups):
                        participant_user = random.choice([p.user for p in trip.participants])
                        
                        meetup = Meetups(
                            trip_id=trip.id,
                            user_id=participant_user.id,
                            content=random.choice([
                                "Meeting at train station",
                                "Airport pickup coordination",
                                "Hotel lobby meetup",
                                "Starting point for walking tour",
                                "Pre-dinner drinks location"
                            ]),
                            location=random.choice([
                                "Central Train Station",
                                "Airport Terminal 1",
                                "Plaza Mayor",
                                "Hotel Lobby",
                                "Metro Station Entrance"
                            ]),
                            city_id=trip.destination_city_id if trip.destination_city_id else cities["Madrid"].id,
                            date=trip.start_date if trip.start_date else date.today() + timedelta(days=10),
                            time=time(random.randint(9, 18), random.choice([0, 30])),
                            status=random.choice(["PLANNING", "PLANNING", "HAPPENING"])
                        )
                        db.session.add(meetup)
                        meetup_count += 1
            db.session.commit()
            print(f"   ✅ Created {meetup_count} meetups")

            # 11. Create Trip Comments
            print("\n💬 Creating trip comments...")
            comment_templates = [
                "This looks amazing! Count me in!",
                "I've been to this place before, it's fantastic!",
                "What time should we meet?",
                "Can we add a vegetarian option?",
                "I know a great spot nearby we should check out.",
                "Is there space for one more person?",
                "Looking forward to this!",
                "Do we need reservations?",
                "I can help with the planning if needed.",
                "This is exactly what I've been looking for!",
                "Would love to join but need to check my schedule.",
                "Great choice of restaurant!",
                "I heard the chef there is amazing.",
                "Can we adjust the time slightly?",
                "Perfect timing for me!",
                "I'll bring some friends if that's okay.",
                "What's the dress code?",
                "Excited to try this cuisine!",
                "I've wanted to visit this place for ages!",
                "Let me know if you need help organizing."
            ]
            
            comment_count = 0
            for trip in trips:
                num_comments = random.randint(2, 8)
                
                # Get potential commenters (participants + some random users)
                potential_commenters = [p.user for p in trip.participants]
                additional_commenters = random.sample(
                    [u for u in users if u not in potential_commenters], 
                    min(3, len(users) - len(potential_commenters))
                )
                potential_commenters.extend(additional_commenters)
                
                for _ in range(min(num_comments, len(potential_commenters))):
                    commenter = random.choice(potential_commenters)
                    
                    comment = TripComment(
                        trip_id=trip.id,
                        author_id=commenter.id,
                        content=random.choice(comment_templates)
                    )
                    db.session.add(comment)
                    comment_count += 1
            db.session.commit()
            print(f"   ✅ Created {comment_count} trip comments")

            # Final Summary
            print("\n" + "=" * 70)
            print("🎉 TEST DATA CREATION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            
            print("\n📊 DATABASE STATISTICS:")
            print(f"   • Users:                 {User.query.count():>4}")
            print(f"   • Cities:                {City.query.count():>4}")
            print(f"   • Neighborhoods:         {Neighborhood.query.count():>4}")
            print(f"   • Trips:                 {Trip.query.count():>4}")
            print(f"   • Trip Stops:            {TripStop.query.count():>4}")
            print(f"   • Interests:             {Interest.query.count():>4}")
            print(f"   • Following:             {FollowingAssociation.query.count():>4}")
            print(f"   • Trip Participants:     {Trip_participants.query.count():>4}")
            print(f"   • Trip Invitations:      {Trip_invitations.query.count():>4}")
            print(f"   • Meetups:               {Meetups.query.count():>4}")
            print(f"   • Trip Comments:         {TripComment.query.count():>4}")
            
            # Sample relationship tests
            print("\n🔗 SAMPLE RELATIONSHIP TESTS:")
            sample_user = users[0]
            print(f"\n   User: {sample_user.name}")
            print(f"   • Interests: {', '.join([i.interest for i in sample_user.interests])}")
            print(f"   • Following: {len(sample_user.following)} users")
            print(f"   • Followers: {len(sample_user.followers)} users")
            print(f"   • Trips Created: {len(sample_user.trips_created)}")
            print(f"   • Trip Participations: {len(sample_user.trip_participations)}")
            print(f"   • Trip Invitations: {len(sample_user.trip_invitations)}")
            
            sample_trip = trips[0]
            print(f"\n   Trip: {sample_trip.title}")
            print(f"   • Participants: {len(sample_trip.participants)}")
            print(f"   • Stops: {len(sample_trip.stops)}")
            print(f"   • Comments: {len(sample_trip.comments)}")
            print(f"   • Meetups: {len(sample_trip.meetups)}")
            print(f"   • Invitations: {len(sample_trip.invitations)}")
            
            print("\n" + "=" * 70)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            db.session.rollback()
            raise e


def clear_test_data():
    """Clear all test data from the database"""
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("🧹 CLEARING ALL TEST DATA")
        print("=" * 70)

        try:
            print("\n   Deleting trip comments...")
            TripComment.query.delete()
            print("   Deleting meetups...")
            Meetups.query.delete()
            print("   Deleting trip stops...")
            TripStop.query.delete()
            print("   Deleting trip participants...")
            Trip_participants.query.delete()
            print("   Deleting trip invitations...")
            Trip_invitations.query.delete()
            print("   Deleting trips...")
            Trip.query.delete()
            print("   Deleting following relationships...")
            FollowingAssociation.query.delete()
            print("   Deleting interests...")
            Interest.query.delete()
            print("   Deleting users...")
            User.query.delete()
            print("   Deleting neighborhoods...")
            Neighborhood.query.delete()
            print("   Deleting cities...")
            City.query.delete()

            db.session.commit()
            
            print("\n" + "=" * 70)
            print("✅ ALL TEST DATA CLEARED SUCCESSFULLY!")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            db.session.rollback()
            raise e


def show_stats():
    """Display database statistics"""
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("📊 DATABASE STATISTICS")
        print("=" * 70)
        
        print(f"\n   Users:                 {User.query.count():>4}")
        print(f"   Cities:                {City.query.count():>4}")
        print(f"   Neighborhoods:         {Neighborhood.query.count():>4}")
        print(f"   Trips:                 {Trip.query.count():>4}")
        print(f"   Trip Stops:            {TripStop.query.count():>4}")
        print(f"   Interests:             {Interest.query.count():>4}")
        print(f"   Following:             {FollowingAssociation.query.count():>4}")
        print(f"   Trip Participants:     {Trip_participants.query.count():>4}")
        print(f"   Trip Invitations:      {Trip_invitations.query.count():>4}")
        print(f"   Meetups:               {Meetups.query.count():>4}")
        print(f"   Trip Comments:         {TripComment.query.count():>4}")
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "clear":
            clear_test_data()
        elif command == "stats":
            show_stats()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python test_data.py [clear|stats]")
    else:
        create_test_data()