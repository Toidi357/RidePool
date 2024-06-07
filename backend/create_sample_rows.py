from config import app, db, bcrypt
# from config import app
from models import User, Ride
from datetime import datetime, timedelta
import random

def add_ratings_to_users(users):
    # Iterate over each user to assign ratings
    for user in users:
        # Each user receives ratings from up to 5 other users
        num_ratings = random.randint(1, 5)
        rated_by_users = random.sample([u for u in users if u.user_id != user.user_id], num_ratings)
        
        # Generate random ratings and append to user's ratings JSON
        # for rater in rated_by_users:
        #     rating = {
        #         "rated_by": rater.user_id,
        #         "rating": random.randint(1, 5),  # Ratings between 1 and 5
        #         "timestamp": datetime.now().isoformat() + 'Z'
        #     }
        #     user.ratings.append(rating)
        
        # Calculate and update average rating for the user
        # if user.ratings:
        #     user.avg_rating = sum(r['rating'] for r in user.ratings) / len(user.ratings)
        # else:
        #     user.avg_rating = None

def create_sample_data():
    with app.app_context():
        db.create_all()

        # Sample Users
        users = []
        for i in range(1, 11):
            user = User(
                username=f'u{i}',
                password=bcrypt.generate_password_hash(f'p{i}').decode('utf-8'),
                first_name=f'FirstName{i}',
                last_name=f'LastName{i}',
                email=f'user{i}@example.com',
                phone_number=f'123456789{i}',
                latitude=37.7749 + i * 0.1,
                longitude=-122.4194 - i * 0.1
            )
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        # Sample Rides
        rides = [
            Ride(
                creator_id=users[0].user_id,
                pickup_longitude=-122.4194,
                pickup_latitude=37.7749,
                destination_longitude=-118.2437,
                destination_latitude=34.0522,
                pickup_threshold=0.5,
                destination_threshold=0.5,
                earliest_pickup_time=datetime.now() + timedelta(hours=1),
                latest_pickup_time=datetime.now() + timedelta(hours=2),
                max_group_size=4,
                description='Ride from SF to LA',
                preferred_apps='Uber, Lyft'
            ),
            Ride(
                creator_id=users[1].user_id,
                pickup_longitude=-74.0060,
                pickup_latitude=40.7128,
                destination_longitude=-73.935242,
                destination_latitude=40.730610,
                pickup_threshold=0.3,
                destination_threshold=0.3,
                earliest_pickup_time=datetime.now() + timedelta(days=1),
                latest_pickup_time=datetime.now() + timedelta(days=1, hours=2),
                max_group_size=3,
                description='Ride from NYC to Brooklyn',
                preferred_apps='Uber'
            ),
            Ride(
                creator_id=users[2].user_id,
                pickup_longitude=-118.2437,
                pickup_latitude=34.0522,
                destination_longitude=-122.4194,
                destination_latitude=37.7749,
                pickup_threshold=0.7,
                destination_threshold=0.7,
                earliest_pickup_time=datetime.now() - timedelta(days=1),
                latest_pickup_time=datetime.now() - timedelta(days=1, hours=1),
                max_group_size=5,
                description='Ride from LA to SF',
                preferred_apps='Lyft'
            ),
            Ride(
                creator_id=users[3].user_id,
                pickup_longitude=-73.935242,
                pickup_latitude=40.730610,
                destination_longitude=-118.2437,
                destination_latitude=34.0522,
                pickup_threshold=0.4,
                destination_threshold=0.4,
                earliest_pickup_time=datetime.now() + timedelta(days=5),
                latest_pickup_time=datetime.now() + timedelta(days=5, hours=4),
                max_group_size=4,
                description='Ride from Brooklyn to LA',
                preferred_apps='Uber, Lyft'
            ),
            Ride(
                creator_id=users[4].user_id,
                pickup_longitude=-122.4194,
                pickup_latitude=37.7749,
                destination_longitude=-74.0060,
                destination_latitude=40.7128,
                pickup_threshold=0.6,
                destination_threshold=0.6,
                earliest_pickup_time=datetime.now() + timedelta(days=10),
                latest_pickup_time=datetime.now() + timedelta(days=10, hours=2),
                max_group_size=6,
                description='Ride from SF to NYC',
                preferred_apps='Uber'
            )
        ]
        db.session.add_all(rides)
        db.session.commit()

        # Add users as members and requesters of different rides
        rides[0].members.append(users[1])
        rides[0].members.append(users[2])
        rides[0].requesters.append(users[3])

        rides[1].members.append(users[0])
        rides[1].requesters.append(users[4])

        rides[2].members.append(users[3])
        rides[2].members.append(users[4])
        rides[2].requesters.append(users[1])

        rides[3].members.append(users[0])
        rides[3].members.append(users[2])
        rides[3].requesters.append(users[4])

        rides[4].members.append(users[0])
        rides[4].members.append(users[2])
        rides[4].requesters.append(users[3])

        add_ratings_to_users(users)

        db.session.commit()

def delete_all_data():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        delete_all_data()
        create_sample_data()
    print("Sample data created successfully.")
