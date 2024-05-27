from flask import request, jsonify, session
from config import app, db, bcrypt
from models import User, Ride
from datetime import datetime

from sqlalchemy import func
from datetime import datetime
from geolocation import get_location
from geopy.distance import distance

from flask_migrate import Migrate
import os

migrate = Migrate(app, db)

app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/test', methods = ['GET']) 
def test():
    return jsonify({'response': 'connection successful'})


@app.route('/register', methods=['POST'])
def register():
    data = request.json

    print(data)

    required_fields = ['username', 'password', 'firstName', 'lastName', 'email', 'phoneNumber']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        phone_number=data['phoneNumber']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    print(data)

    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Both username and password are required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        session['user_id'] = user.user_id

        # Capture the location

        location_data = get_location()
        print(location_data)
        user.latitude = location_data['location']['lat']
        user.longitude = location_data['location']['lng']
        db.session.commit()
        
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"}), 200

@app.route('/users/profile', methods=['PUT'])
def update_user_profile():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    user = User.query.get_or_404(current_user_id)

    data = request.json
    user.first_name = data.get('firstName', user.first_name)
    user.last_name = data.get('lastName', user.last_name)
    user.email = data.get('email', user.email)
    user.phone_number = data.get('phoneNumber', user.phone_number)

    db.session.commit()

    return jsonify({"message": "User profile updated successfully"}), 200

@app.route('/rides', methods=['POST'])
def create_ride():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    data = request.json

    required_fields = ['pickupLongitude', 'pickupLatitude', 'destinationLongitude', 'destinationLatitude', 'pickupThreshold', 'destinationThreshold', 'earliestArrivalTime', 'latestArrivalTime', 'maxGroupSize', 'private', 'description', 'preferredApps']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    new_ride = Ride(
        creator_id=current_user_id,
        pickup_longitude=data['pickupLongitude'],
        pickup_latitude=data['pickupLatitude'],
        destination_longitude=data['destinationLongitude'],
        destination_latitude=data['destinationLatitude'],
        pickup_threshold=data['pickupThreshold'],
        destination_threshold=data['destinationThreshold'],
        earliest_arrival_time=datetime.fromisoformat(data['earliestArrivalTime']),
        latest_arrival_time=datetime.fromisoformat(data['latestArrivalTime']),
        max_group_size=data['maxGroupSize'],
        private=data['private'],
        description=data['description'],
        preferred_apps=data['preferredApps']
    )
    db.session.add(new_ride)
    db.session.commit()
    return jsonify(new_ride.to_json()), 201

@app.route('/rides', methods=['GET'])
def get_rides(rideFilter, pickupThreshold = 0):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    rides = Ride.query.filter(
        (Ride.earliest_arrival_time > datetime.now()) & # obviously, need a better way of checking if a ride is complete or not. maybe a boolean status for completion set asynch after time passes latest_arrival_time
        (Ride.creator_id != current_user_id) &
        (func.count(Ride.members) < Ride.max_group_size)
    ).group_by(Ride.ride_id).all()

    current_time = datetime.now()
    sortedRide = []
    if rideFilter == 'location':
        sortedRide = sorted(rides, key=lambda ride: distance((User.latitude, User.longitude),(ride.pickup_latitude, ride.pickup_longitude)).miles)
    elif rideFilter == 'earliestArrivalTime':
        sortedRide = sorted(rides, key=lambda ride: abs((ride.earliest_arrival_time - current_time).total_seconds()))
    elif rideFilter == 'latestArrivalTime':
        sortedRide = sorted(rides, key=lambda ride: abs((ride.latest_arrival_time - current_time).total_seconds()))
    elif rideFilter == 'private':
        for r in rides:
            if r.private == True:
                sortedRide.append(r)
    elif rideFilter == 'public':
        for r in rides:
            if r.private == False:
                sortedRide.append(r)
    elif rideFilter == 'pickupThreshold':
        sortedRide = [ride for ride in rides if distance((User.latitude, User.longitude), (ride.latitude, ride.longitude)).miles <= pickupThreshold]


    return jsonify([ride.to_json() for ride in sortedRide])

@app.route('/rides/<int:ride_id>', methods=['PUT'])
def update_ride(ride_id):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    ride = Ride.query.get_or_404(ride_id)
    if ride.creator_id != current_user_id:
        return jsonify({"message": "Permission denied"}), 403
    if len(ride.members) > 1:
        return jsonify({"message": "Cannot modify ride with other members"}), 403
    data = request.json
    ride.pickup_longitude = data.get('pickupLongitude', ride.pickup_longitude)
    ride.pickup_latitude = data.get('pickupLatitude', ride.pickup_latitude)
    ride.destination_longitude = data.get('destinationLongitude', ride.destination_longitude)
    ride.destination_latitude = data.get('destinationLatitude', ride.destination_latitude)
    ride.pickup_threshold = data.get('pickupThreshold', ride.pickup_threshold)
    ride.destination_threshold = data.get('destinationThreshold', ride.destination_threshold)
    ride.earliest_arrival_time = datetime.fromisoformat(data.get('earliestArrivalTime', ride.earliest_arrival_time.isoformat()))
    ride.latest_arrival_time = datetime.fromisoformat(data.get('latestArrivalTime', ride.latest_arrival_time.isoformat()))
    ride.max_group_size = data.get('maxGroupSize', ride.max_group_size)
    ride.private = data.get('private', ride.private)
    ride.description = data.get('description', ride.description)
    ride.preferred_apps = data.get('preferredApps', ride.preferred_apps)
    db.session.commit()
    return jsonify(ride.to_json())

@app.route('/rides/<int:ride_id>/join', methods=['POST'])
def join_ride(ride_id):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    ride = Ride.query.get_or_404(ride_id)
    user = User.query.get_or_404(current_user_id)

    if user in ride.members:
        return jsonify({"message": "User already joined this ride"}), 400

    if len(ride.members) >= ride.max_group_size:
        return jsonify({"message": "Ride is full. Cannot join."}), 400

    conflicting_rides = [user_ride for user_ride in user.rides if ride_conflicts(ride, user_ride)]
    if conflicting_rides:
        return jsonify({"message": "User has conflicting upcoming ride(s). Cannot join."}), 400

    ride.members.append(user)
    db.session.commit()
    return jsonify({"message": "User joined the ride successfully"}), 200

def ride_conflicts(ride1, ride2):
    return ride1.latest_arrival_time > ride2.earliest_arrival_time and ride2.latest_arrival_time > ride1.earliest_arrival_time

@app.route('/rides/<int:ride_id>/leave', methods=['POST'])
def leave_ride(ride_id):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    ride = Ride.query.get_or_404(ride_id)
    user = User.query.get_or_404(current_user_id)

    if user not in ride.members:
        return jsonify({"message": "User is not a member of this ride"}), 400

    if len(ride.members) == 1:
        db.session.delete(ride)
        db.session.commit()
        return jsonify({"message": "User left the ride successfully and the ride has been deleted"}), 200

    ride.members.remove(user)
    db.session.commit()
    return jsonify({"message": "User left the ride successfully"}), 200

@app.route('/rides/<int:ride_id>/members', methods=['GET'])
def get_ride_members(ride_id):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    ride = Ride.query.get_or_404(ride_id)
    members = ride.members
    return jsonify([member.to_json() for member in members]), 200

@app.route('/users/rides', methods=['GET'])
def get_user_rides():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    user = User.query.get_or_404(current_user_id)
    rides = user.rides
    return jsonify([ride.to_json() for ride in rides]), 200

@app.route('/users/upcoming_rides', methods=['GET'])
def get_user_upcoming_rides():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    user = User.query.get_or_404(current_user_id)
    upcoming_rides = [ride for ride in user.rides if ride.latest_arrival_time > datetime.now()]
    return jsonify([ride.to_json() for ride in upcoming_rides]), 200

if __name__ == "__main__":
    port = 5000
    app.run(debug=True, host='0.0.0.0')



'''
Supported functionalities:

User: 
- register
- login
- logout
- update profile info (in react, use this endpoint with a <form></form>)
- create new ride 
- fetch all posted rides that have not occurred yet and not created by user and not full [for displaying feed]
- update ride created by user (only if creator is only member of ride to prevent conflicts for other members)
- join existing ride if no conflicts with other ride commitments and there's space in the ride and not already member of ride
- leave ride they are a part of (deletes ride if they're the only member)
- get ride members for a specific ride (allow for all rides so users can see members of rides before joining, update)
- get all rides they are / were part of
- get upcoming ride commitments (used to check for conflicts)

'''
