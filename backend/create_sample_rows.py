from config import db, bcrypt, app
from models import User, Ride
from datetime import datetime, timedelta
import random

# Sample location data (latitude, longitude)
locations = [
    {"latitude": 40.712776, "longitude": -74.005974},  # New York City, NY
    {"latitude": 34.052235, "longitude": -118.243683}, # Los Angeles, CA
    {"latitude": 41.878113, "longitude": -87.629799},  # Chicago, IL
    {"latitude": 29.760427, "longitude": -95.369804},  # Houston, TX
    {"latitude": 33.448376, "longitude": -112.074036}, # Phoenix, AZ
    {"latitude": 39.739236, "longitude": -104.990251}, # Denver, CO
    {"latitude": 47.606209, "longitude": -122.332071}, # Seattle, WA
    {"latitude": 38.907192, "longitude": -77.036873},  # Washington, D.C.
    {"latitude": 37.774929, "longitude": -122.419418}, # San Francisco, CA
    {"latitude": 25.761680, "longitude": -80.191790}   # Miami, FL
]

# Concise ride descriptions
descriptions = [
    "Girls Only",
    "Silent Ride",
    "Tell Stories",
    "Music Ride",
    "Adventure Time",
    "Quick Ride",
    "Chill Ride",
    "Book Club",
    "Food Talk",
    "Tech Talk"
]

# Sample names
first_names = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Martinez", "Lee"]

def delete_all_data():
    """Delete all data from the database and recreate tables."""
    db.drop_all()
    db.create_all()

def create_sample_data():
    """Create sample users and rides in the database."""
    # Create sample users
    users = []
    for i in range(1, 11):
        username = f'u{i}'
        password = bcrypt.generate_password_hash(f'p{i}').decode('utf-8')
        rating_sum = random.uniform(0, 50)
        num_ratings = 10
        avg_rating = rating_sum / num_ratings if num_ratings > 0 else None
        user = User(
            username=username,
            password=password,
            first_name=first_names[i-1],
            last_name=last_names[i-1],
            email=f'user{i}@example.com',
            phone_number=f'123456789{i}',
            latitude=locations[i % len(locations)]['latitude'],
            longitude=locations[i % len(locations)]['longitude'],
            rating_sum=rating_sum,
            num_ratings=num_ratings,
            avg_rating=avg_rating
        )
        users.append(user)
        db.session.add(user)
    db.session.commit()  # Commit users first so they have IDs

    # Create sample rides
    for j in range(1, 11):
        if j % 2 == 0:
            ride_creator_id = 1  # Make User 1 the creator for even-numbered rides
        else:
            ride_creator_id = random.randint(2, 10)  # Use a random user except User 1 for odd-numbered rides
        
        pickup_location = random.choice(locations)
        destination_location = random.choice(locations)
        
        # Set the ride time, half in the past
        if j <= 5:
            earliest_pickup_time = datetime.now() - timedelta(days=random.randint(1, 30))
            latest_pickup_time = earliest_pickup_time + timedelta(hours=random.randint(1, 3))
        else:
            earliest_pickup_time = datetime.now() + timedelta(days=random.randint(1, 10))
            latest_pickup_time = earliest_pickup_time + timedelta(hours=random.randint(1, 3))
        
        ride = Ride(
            creator_id=ride_creator_id,
            pickup_longitude=pickup_location['longitude'],
            pickup_latitude=pickup_location['latitude'],
            destination_longitude=destination_location['longitude'],
            destination_latitude=destination_location['latitude'],
            pickup_threshold=random.uniform(0.1, 2.0),
            destination_threshold=random.uniform(0.1, 2.0),
            earliest_pickup_time=earliest_pickup_time,
            latest_pickup_time=latest_pickup_time,
            max_group_size=random.randint(2, 5),
            description=random.choice(descriptions),
            preferred_apps='Any'
        )
        db.session.add(ride)
        db.session.flush()  # Ensure ride_id is set before using .append()

        # Add random members to the ride
        num_members = random.randint(1, 3)
        for _ in range(num_members):
            random_member = random.choice(users[:3])  # Select a random user except User 1
            if random_member not in ride.members:
                ride.members.append(random_member)

        # Optionally add random requesters to the ride
        num_requesters = random.randint(0, 2)
        for _ in range(num_requesters):
            random_requester = random.choice(users[1:])  # Select a random user except User 1
            if random_requester not in ride.requesters:
                ride.requesters.append(random_requester)

    db.session.commit()
    print("Sample data created successfully.")

if __name__ == '__main__':
    with app.app_context():
        delete_all_data()
        create_sample_data()
