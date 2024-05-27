from config import db, bcrypt
from app import app
from models import User, Ride
from datetime import datetime

from werkzeug.security import generate_password_hash
from datetime import timedelta

def create_sample_data():
    with app.app_context():
        db.create_all()

        # Sample Users
        user1 = User(
            username='A',
            password=bcrypt.generate_password_hash('B').decode('utf-8'),
            first_name='C',
            last_name='D',
            email='E',
            phone_number='1234567890',
            latitude=37.7749,
            longitude=-122.4194
        )
        user2 = User(
            username='user2',
            password=bcrypt.generate_password_hash('p2').decode('utf-8'),
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            phone_number='0987654321',
            latitude=34.0522,
            longitude=-118.2437
        )
        user3 = User(
            username='user3',
            password=bcrypt.generate_password_hash('p3').decode('utf-8'),
            first_name='Alice',
            last_name='Johnson',
            email='alice@example.com',
            phone_number='1231231234',
            latitude=40.7128,
            longitude=-74.0060
        )
        db.session.add_all([user1, user2, user3])
        db.session.commit()

        # Sample Rides
        ride1 = Ride(
            creator_id=user1.user_id,
            pickup_longitude=-122.4194,
            pickup_latitude=37.7749,
            destination_longitude=-118.2437,
            destination_latitude=34.0522,
            pickup_threshold=0.5,
            destination_threshold=0.5,
            earliest_pickup_time=datetime.now() - timedelta(days=1),
            latest_pickup_time=datetime.now() - timedelta(days=1),
            max_group_size=4,
            private=False,
            description='Ride from SF to LA',
            preferred_apps='Uber, Lyft'
        )
        ride2 = Ride(
            creator_id=user2.user_id,
            pickup_longitude=-74.0060,
            pickup_latitude=40.7128,
            destination_longitude=-73.935242,
            destination_latitude=40.730610,
            pickup_threshold=0.3,
            destination_threshold=0.3,
            earliest_pickup_time=datetime.now() - timedelta(days=2),
            latest_pickup_time=datetime.now() - timedelta(days=2),
            max_group_size=3,
            private=True,
            description='Ride from NYC to Brooklyn',
            preferred_apps='Uber'
        )
        ride3 = Ride(
            creator_id=user3.user_id,
            pickup_longitude=-118.2437,
            pickup_latitude=34.0522,
            destination_longitude=-122.4194,
            destination_latitude=37.7749,
            pickup_threshold=0.7,
            destination_threshold=0.7,
            earliest_pickup_time=datetime(2023, 5, 25, 15, 0),
            latest_pickup_time=datetime(2023, 5, 25, 18, 0),
            max_group_size=5,
            private=False,
            description='Ride from LA to SF',
            preferred_apps='Lyft'
        )
        ride4 = Ride(
            creator_id=user1.user_id,
            pickup_longitude=-73.935242,
            pickup_latitude=40.730610,
            destination_longitude=-118.2437,
            destination_latitude=34.0522,
            pickup_threshold=0.4,
            destination_threshold=0.4,
            earliest_pickup_time=datetime(2023, 6, 10, 10, 0),
            latest_pickup_time=datetime(2023, 6, 10, 14, 0),
            max_group_size=4,
            private=True,
            description='Ride from Brooklyn to LA',
            preferred_apps='Uber, Lyft'
        )
        ride5 = Ride(
            creator_id=user2.user_id,
            pickup_longitude=-122.4194,
            pickup_latitude=37.7749,
            destination_longitude=-74.0060,
            destination_latitude=40.7128,
            pickup_threshold=0.6,
            destination_threshold=0.6,
            earliest_pickup_time=datetime.now() + timedelta(days=30),
            latest_pickup_time=datetime.now() + timedelta(days=30),
            max_group_size=6,
            private=False,
            description='Ride from SF to NYC',
            preferred_apps='Uber'
        )
        db.session.add_all([ride1, ride2, ride3, ride4, ride5])
        db.session.commit()

        # Add users as members of different rides
        ride1.members.append(user2)
        ride1.members.append(user3)
        ride2.members.append(user1)
        ride3.members.append(user1)
        ride3.members.append(user2)
        ride4.members.append(user3)
        ride5.members.append(user1)
        ride5.members.append(user3)
        db.session.commit()



def delete_all_data():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        delete_all_data()
        create_sample_data()
    print("Sample data created successfully.")