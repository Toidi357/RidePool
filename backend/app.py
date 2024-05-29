from flask import request, jsonify, session
from config import app, db, bcrypt
from models import User, Ride, BlacklistToken
from datetime import datetime
import logging

from dateutil import parser

from sqlalchemy import func
from datetime import datetime
from geolocation import get_location
from geopy.distance import distance

from flask_migrate import Migrate
migrate = Migrate(app, db)


logging.basicConfig(filename = 'app.log', level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')

class Unauthorized(Exception):
    def __init__(self, message):
        super().__init__(message)

def check_authentication(request) -> User:
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            raise Unauthorized('Bearer token malformed.')
    else:
        auth_token = ''
    if auth_token: # means user *has* a token
        # resp should contain an object with the decoded token details
        # if its a string, that means its an error
        resp = User.decode_auth_token(auth_token)
        
        if not isinstance(resp, str):
            user = User.query.filter_by(username=resp['sub']).first()
            return user
        
        # special error message if token is expired
        if resp == 'Signature expired. Please log in again.':
            raise Unauthorized(resp)
    
    raise Unauthorized('Unauthorized')

@app.route('/test', methods = ['GET']) 
def test():
    return jsonify({'response': 'connection successful'})

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    logging.info(f"Received registration request: {data}")

    print(data)

    required_fields = ['username', 'password', 'firstName', 'lastName', 'email', 'phoneNumber']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # check if user already exists
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({"error": f"User already exists. Please log in."}), 409

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
    logging.info(f"User registered succesfully: {new_user.username}")
    auth_token = new_user.encode_auth_token(new_user.username)
    return jsonify({"message": "User registered successfully", "auth_token": auth_token}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    print(data)
    logging.info(f"Received login request data: {data}")

    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Both username and password are required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        auth_token = user.encode_auth_token(user.username)
        
        if auth_token:
            responseObject = {
                'message': 'Successfully logged in.',
                'auth_token': auth_token,
            }
            # Capture the location
            location_data = get_location()
            print(location_data)
            user.latitude = location_data['location']['lat']
            
            user.longitude = location_data['location']['lng']
            print("RESPONSE OBJ")
            print(responseObject)

            return jsonify(responseObject), 200
        
        logging.info(f"User {user.username} logged in succesfully")
        return jsonify({"message": "Login successful"}), 200
    
    logging.warning("Invalid login credentials")
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout', methods=['GET'])
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    'message': 'Logout successful'
                }
                return jsonify(responseObject), 200
            except Exception as e:
                return jsonify({'message': 'Error'}), 500
            
    logging.info("User logged out succesfully")
    return jsonify({"message": "Unauthorized"}), 401

# aight we really getting into the weeds with this one
@app.route('/refresh_token', methods=['GET'])
def generate_refresh_token():
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    try:
        auth_token = user.encode_auth_token(user.username)
        return jsonify({"auth_token": auth_token}), 200
    except:
        return jsonify({"Internal Server Error"}), 500


@app.route('/profile', methods=['GET'])
def get_user_profile():
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})
    
    responseObject = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
    }
    return jsonify(responseObject), 200

@app.route('/profile', methods=['POST'])
def update_user_profile():
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    data = request.json

    logging.info(f"User {current_user_id} is updating their profile")
    logging.info(f"Updated profile data received: {data}")
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.phone_number = data.get('phone_number', user.phone_number)

    db.session.commit()

    logging.info("User profile updated succesfully")

    return jsonify({"message": "User profile updated successfully"}), 200

@app.route('/rides', methods=['POST'])
def create_ride():

    # FOR TESTING PURPOSES ONLY, current_user_id IS SET TO 1.
    # PLEASE CHANGE THIS CODE TO WHATEVER THE CORRECT AUTHENTICATION IS.

    current_user_id = 1

    # if 'user_id' not in session:
    #     return jsonify({"message": "Unauthorized"}), 401

    # current_user_id = session['user_id']

    data = request.json

    logging.info(f"User {current_user_id} is attempting to create a new ride")

    logging.info (f"Received data for ride creation: {data}")

    required_fields = ['pickupLongitude', 'pickupLatitude', 'destinationLongitude', 'destinationLatitude', 'pickupThreshold', 'destinationThreshold', 'earliestPickupTime', 'latestPickupTime', 'maxGroupSize', 'private', 'description'] # , 'preferredApps'

    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")
            logging.warning(f"Missing required field: {field}")
            return jsonify({"error": f"Missing required field: {field}"}), 400

    new_ride = Ride(
        creator_id=current_user_id,
        pickup_longitude=data['pickupLongitude'],
        pickup_latitude=data['pickupLatitude'],
        destination_longitude=data['destinationLongitude'],
        destination_latitude=data['destinationLatitude'],
        pickup_threshold=data['pickupThreshold'],
        destination_threshold=data['destinationThreshold'],
        # earliest_arrival_time=datetime.fromisoformat(data['earliestArrivalTime']),
        # latest_arrival_time=datetime.fromisoformat(data['latestArrivalTime']),
        earliest_pickup_time=parser.isoparse(data['earliestPickupTime']),
        latest_pickup_time=parser.isoparse(data['latestPickupTime']),
        max_group_size=data['maxGroupSize'],
        private=data['private'],
        description=data['description'],
        # preferred_apps=data['preferredApps']
    )

    # Need to set up proper associations!
    # new_ride.creator.append(user)


    db.session.add(new_ride)
    db.session.commit()

    logging.info (f"New ride created succesfully: {new_ride.to_json()}")
    return jsonify(new_ride.to_json()), 201

@app.route('/rides', methods=['GET'])
def get_rides(rideFilter, pickupThreshold = 0):
    if 'user_id' not in session:
        logging.warning("Unauthorized access attempt to get rides")
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    logging.info(f"User {current_user_id} is attempting to retreive with filter: {rideFilter} and pickup threshold: {pickupThreshold}")
    rides = Ride.query.filter(
        (Ride.earliest_pickup_time > datetime.now()) & # obviously, need a better way of checking if a ride is complete or not. maybe a boolean status for completion set asynch after time passes latest_arrival_time
        (Ride.creator_id != current_user_id) &
        (func.count(Ride.members) < Ride.max_group_size)
    ).group_by(Ride.ride_id).all()

    logging.info(f"Retrieved {len(rides)} rides from the database")

    current_time = datetime.now()
    sortedRide = []
    if rideFilter == 'location':
        logging.info("Sorting rides by location")
        sortedRide = sorted(rides, key=lambda ride: distance((User.latitude, User.longitude),(ride.pickup_latitude, ride.pickup_longitude)).miles)
    elif rideFilter == 'earliestPickupTime':
        logging.info("Sorting rides by earliest pickup time")
        sortedRide = sorted(rides, key=lambda ride: abs((ride.earliest_pickup_time - current_time).total_seconds()))
    elif rideFilter == 'latestPickupTime':
        logging.info("Sorting rides by latest pickup time")
        sortedRide = sorted(rides, key=lambda ride: abs((ride.latest_pickup_time - current_time).total_seconds()))
    elif rideFilter == 'private':
        logging.info("Filtering rides to show only private rides")
        for r in rides:
            if r.private == True:
                sortedRide.append(r)
    elif rideFilter == 'public':
        logging.info("Filtering rides to show only public rides")
        for r in rides:
            if r.private == False:
                sortedRide.append(r)
    elif rideFilter == 'pickupThreshold':
        logging.info(f"Filtering rides within a pickup threshold of {pickupThreshold} miles")
        sortedRide = [ride for ride in rides if distance((User.latitude, User.longitude), (ride.latitude, ride.longitude)).miles <= pickupThreshold]

    logging.info(f"Returning {len(sortedRide)} sorted and filtered rides")

    return jsonify([ride.to_json() for ride in sortedRide])

@app.route('/rides/<int:ride_id>', methods=['PUT'])
def update_ride(ride_id):
    if 'user_id' not in session:
        logging.warning("Unauthorized access attempt to update ride")
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    logging.info(f"User {current_user_id} is attempting to update ride {ride_id}")
    ride = Ride.query.get_or_404(ride_id)
    logging.info(f"Ride {ride_id} retrieved from the database")

    if ride.creator_id != current_user_id:
        logging.warning(f"User {current_user_id} does not have permission to update ride {ride_id}")
        return jsonify({"message": "Permission denied"}), 403
    if len(ride.members) > 1:
        logging.warning(f"Ride {ride_id} cannot be modified because it has other members")
        return jsonify({"message": "Cannot modify ride with other members"}), 403
    data = request.json
    logging.info(f"Updating ride {ride_id} with data: {data}")

    ride.pickup_longitude = data.get('pickupLongitude', ride.pickup_longitude)
    ride.pickup_latitude = data.get('pickupLatitude', ride.pickup_latitude)
    ride.destination_longitude = data.get('destinationLongitude', ride.destination_longitude)
    ride.destination_latitude = data.get('destinationLatitude', ride.destination_latitude)
    ride.pickup_threshold = data.get('pickupThreshold', ride.pickup_threshold)
    ride.destination_threshold = data.get('destinationThreshold', ride.destination_threshold)
    ride.earliest_pickup_time = datetime.fromisoformat(data.get('earliestArrivalTime', ride.earliest_pickup_time.isoformat()))
    ride.latest_pickup_time = datetime.fromisoformat(data.get('latestArrivalTime', ride.latest_pickup_time.isoformat()))
    ride.max_group_size = data.get('maxGroupSize', ride.max_group_size)
    ride.private = data.get('private', ride.private)
    ride.description = data.get('description', ride.description)
    # ride.preferred_apps = data.get('preferredApps', ride.preferred_apps)
    db.session.commit()
    logging.info(f"Ride {ride_id} updated succesfully")
    return jsonify(ride.to_json())

@app.route('/rides/<int:ride_id>/join', methods=['POST'])
def join_ride(ride_id):
    if 'user_id' not in session:
        logging.warning("Unauthorized access attempt to join ride")
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    logging.info(f"User {current_user_id} is attempting to join ride {ride_id}")
    ride = Ride.query.get_or_404(ride_id)
    logging.info(f"Ride {ride_id} retrieved from the database")
    user = User.query.get_or_404(current_user_id)
    logging.info(f"User {current_user_id} retrieved from the database")

    if user in ride.members:
        logging.warning(f"User {current_user_id} already joined ride {ride_id}")
        return jsonify({"message": "User already joined this ride"}), 400

    if len(ride.members) >= ride.max_group_size:
        logging.warning(f"Ride {ride_id} is full, user {current_user_id} cannot join")
        return jsonify({"message": "Ride is full. Cannot join."}), 400

    conflicting_rides = [user_ride for user_ride in user.rides if ride_conflicts(ride, user_ride)]
    if conflicting_rides:
        logging.warning(f"User {current_user_id} has conflicting upcoming rides and cannot join ride {ride_id}")
        return jsonify({"message": "User has conflicting upcoming ride(s). Cannot join."}), 400

    logging.info(f"User {current_user_id} is joining ride {ride_id}")

    ride.members.append(user)
    db.session.commit()

    logging.info(f"User {current_user_id} joined ride {ride_id} succesfully")
    return jsonify({"message": "User joined the ride successfully"}), 200

def ride_conflicts(ride1, ride2):
    logging.info(f"Checking for conflicts between {ride1.ride_id} and {ride2.ride_id}")
    return ride1.latest_pickup_time > ride2.earliest_pickup_time and ride2.latest_pickup_time > ride1.earliest_pickup_time

@app.route('/rides/<int:ride_id>/leave', methods=['POST'])
def leave_ride(ride_id):
    if 'user_id' not in session:
        logging.warning("Unauthorized access attempt to leave ride")
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    ride = Ride.query.get_or_404(ride_id)
    user = User.query.get_or_404(current_user_id)

    logging.info(f"User {current_user_id} attempting to leave ride {ride_id}")

    if user not in ride.members:
        logging.warning(f"User {current_user_id} is not a member of ride {ride_id}")
        return jsonify({"message": "User is not a member of this ride"}), 400

    if len(ride.members) == 1:
        db.session.delete(ride)
        db.session.commit()
        logging.info(f"User {current_user_id} left ride {ride_id} and the ride has been deleted")
        return jsonify({"message": "User left the ride successfully and the ride has been deleted"}), 200

    ride.members.remove(user)
    db.session.commit()
    logging.info(f"User {current_user_id} left ride {ride_id} successfully")
    return jsonify({"message": "User left the ride successfully"}), 200

@app.route('/rides/<int:ride_id>/members', methods=['GET'])
def get_ride_members(ride_id):
    if 'user_id' not in session:
        logging.warning(f"Unauthorized access attempt to get members of ride {ride_id}")
        return jsonify({"message": "Unauthorized"}), 401

    logging.info(f"User {session['user_id']} attempting to get members of ride {ride_id}")

    ride = Ride.query.get_or_404(ride_id)
    members = ride.members

    logging.info(f"User {session['user_id']} successfully retrieved members of ride {ride_id}")
    return jsonify([member.to_json() for member in members]), 200

@app.route('/users/rides', methods=['GET', 'POST'])
def get_user_rides():
    # FOR TESTING PURPOSES ONLY, current_user_id IS SET TO 1.
    # PLEASE CHANGE THIS CODE TO WHATEVER THE CORRECT AUTHENTICATION IS.

    current_user_id = 1
    logging.info(f"Request received for user {current_user_id}")

    print("request received for user 1")

    data = request.json
    ride_type = data.get('time', 'all')  # Get the type parameter from the request, default to 'all'  
    logging.info(f"Fetching data for user {current_user_id}") 

    user = User.query.get_or_404(current_user_id)
    created_rides = user.created_rides
    member_rides = user.rides

    logging.info(f"User {current_user_id} data retrieved. Filtering rides by type: {ride_type}")

    print(user)

    now = datetime.now()

    def filter_rides(rides, ride_type):
        if ride_type == 'current':
            return [ride for ride in rides if ride.latest_pickup_time > now]
        elif ride_type == 'history':
            return [ride for ride in rides if ride.latest_pickup_time <= now]
        else:  # 'all'
            return rides

    filtered_created_rides = filter_rides(created_rides, ride_type)
    filtered_member_rides = filter_rides(member_rides, ride_type)

    logging.info(f"Rides filtered  for user {current_user_id}: {len(filtered_created_rides)} created, {len(filtered_member_rides)} joined")

    return jsonify({
        "created_rides": [ride.to_json() for ride in filtered_created_rides],
        "member_rides": [ride.to_json() for ride in filtered_member_rides]
    }), 200

@app.route('/users/upcoming_rides', methods=['GET'])
def get_user_upcoming_rides():
    if 'user_id' not in session:
        logging.warning("Unauthorized access attempt to get upcoming rides.")
        return jsonify({"message": "Unauthorized"}), 401

    current_user_id = session['user_id']
    logging.info(f"Fetching upcoming rides for user {current_user_id}")
    user = User.query.get_or_404(current_user_id)
    upcoming_rides = [ride for ride in user.rides if ride.latest_pickup_time > datetime.now()]

    logging.info(f"Upcoming rides filtered for user {current_user_id}")
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
