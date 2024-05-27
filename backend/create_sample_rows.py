from config import db
from app import app
from models import User, Ride
from datetime import datetime

def create_sample_data():
    with app.app_context():
        db.create_all()

        # Sample Users
        user1 = User(
            username='A',
            password='$2b$12$crZRVBVXBdAveq/d2KNcVODPMS2DQejbD1WGfOKw59/x0CEhPC6c2', # this is hashed from "B"
            first_name='C',
            last_name='D',
            email='E',
            phone_number='1234567890',
            latitude=37.7749,
            longitude=-122.4194
        )

        # Sample Rides
        ride1 = Ride(
            creator=user1,
            pickup_longitude=-122.4194,
            pickup_latitude=37.7749,
            destination_longitude=-118.2437,
            destination_latitude=34.0522,
            pickup_threshold=0.5,
            destination_threshold=0.5,
            earliest_pickup_time=datetime.now(),
            latest_pickup_time=datetime.now(),
            max_group_size=4,
            private=False,
            description='Ride from SF to LA',
            preferred_apps='Uber, Lyft'
        )

        # for later
        # ride1.members.append(user2)

        # Add to session
        db.session.add(user1)
        db.session.add(ride1)

        # Commit session
        db.session.commit()

if __name__ == '__main__':
    create_sample_data()
    print("Sample data created successfully.")