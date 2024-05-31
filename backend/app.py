from flask import request, jsonify
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
        print("attempting to decode token "+ auth_token)
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
    print("login attempt")

    data = request.json

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
    print("invalid login credentials")
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

    logging.info(f"User {user.username} is updating their profile")
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
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    data = request.json

    logging.info(f"User {user.username} is attempting to create a new ride")

    logging.info (f"Received data for ride creation: {data}")

    required_fields = ['pickupLongitude', 'pickupLatitude', 'destinationLongitude', 'destinationLatitude', 'pickupThreshold', 'destinationThreshold', 'earliestPickupTime', 'latestPickupTime', 'maxGroupSize', 'description'] # , 'preferredApps'

    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")
            logging.warning(f"Missing required field: {field}")
            return jsonify({"error": f"Missing required field: {field}"}), 400

    new_ride = Ride(
        creator_id=user.user_id,
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
def get_rides():
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    logging.info(f"User {user.username} is attempting to retrieve rides with filters and sort by {sort_by}")

    data = request.json
    desired_pickup_latitude = data.get('desiredPickupLatitude', User.latitude)
    desired_pickup_longitude = data.get('desiredPickupLongitude', User.longitude)
    desired_destination_latitude = data.get('desiredDestinationLatitude')
    desired_destination_longitude = data.get('desiredDestinationLongitude')
    min_date = data.get('minDate', datetime.now())
    max_date = data.get('maxDate', datetime.max)
    pickup_radius_threshold = data.get('pickupRadiusThreshold', float('inf'))
    dropoff_radius_threshold = data.get('dropoffRadiusThreshold', float('inf'))
    sort_by = data.get('sortBy', None)

    if not desired_destination_latitude or not desired_destination_longitude:
        return jsonify({"error": "Missing desired destination location"}), 400
    
    rides = Ride.query.filter(
        (Ride.earliest_pickup_time >= min_date) &
        (Ride.latest_pickup_time <= max_date) &
        (Ride.creator_id != user.user_id) &
        (func.count(Ride.members) < Ride.max_group_size)
    ).all()

    logging.info(f"Retrieved {len(rides)} rides from the database")

    # filter by radii
    filtered_rides = [
        ride for ride in rides
        if distance((desired_pickup_latitude, desired_pickup_longitude),
                    (ride.pickup_latitude, ride.pickup_longitude)).miles <= pickup_radius_threshold and
           distance((desired_destination_latitude, desired_destination_longitude),
                    (ride.destination_latitude, ride.destination_longitude)).miles <= dropoff_radius_threshold
    ]

    logging.info(f"Filtered down to {len(filtered_rides)} rides based on radius thresholds")

    # sort filtered rides by key
    if sort_by == 'pickup_location':
        sorted_rides = sorted(filtered_rides, key=lambda ride: distance((desired_pickup_latitude, desired_pickup_longitude),
                                                                        (ride.pickup_latitude, ride.pickup_longitude)).miles)
    elif sort_by == 'destination_location':
        sorted_rides = sorted(filtered_rides, key=lambda ride: distance((desired_destination_latitude, desired_destination_longitude),
                                                                        (ride.destination_latitude, ride.destination_longitude)).miles)
    elif sort_by == 'pickup_time':
        sorted_rides = sorted(filtered_rides, key=lambda ride: ride.earliest_pickup_time)
    elif sort_by == 'dropoff_time':
        sorted_rides = sorted(filtered_rides, key=lambda ride: ride.latest_dropoff_time)
    else: # no valid sorting key provided
        sorted_rides = filtered_rides

    logging.info(f"Returning {len(sorted_rides)} sorted rides")

    return jsonify([ride.to_json() for ride in sorted_rides])


@app.route('/rides/<int:ride_id>', methods=['PUT'])
def update_ride(ride_id):
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    logging.info(f"User {user.username} is attempting to update ride {ride_id}")
    ride = Ride.query.get_or_404(ride_id)
    logging.info(f"Ride {ride_id} retrieved from the database")

    if ride.creator_id != user.user_id:
        logging.warning(f"User {user.username} does not have permission to update ride {ride_id}")
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
    ride.description = data.get('description', ride.description)
    # ride.preferred_apps = data.get('preferredApps', ride.preferred_apps)
    db.session.commit()
    logging.info(f"Ride {ride_id} updated succesfully")
    return jsonify(ride.to_json())

@app.route('/rides/<int:ride_id>/join', methods=['POST'])
def join_ride(ride_id):
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    current_user_id = user.user_id
    logging.info(f"User {current_user_id} is attempting to join ride {ride_id}")
    ride = Ride.query.get_or_404(ride_id)
    logging.info(f"Ride {ride_id} retrieved from the database")
    user = User.query.get_or_404(user.username)
    logging.info(f"User {user.username} retrieved from the database")

    logging.info(f"User {user.username} is requesting to join ride {ride_id}")

    if user in ride.members:
        logging.warning(f"User {user.username} already joined ride {ride_id}")
        return jsonify({"message": "User already joined this ride"}), 400

    if len(ride.members) >= ride.max_group_size:
        logging.warning(f"Ride {ride_id} is full, user {user.username} cannot join")
        return jsonify({"message": "Ride is full. Cannot join."}), 400

    conflicting_rides = [user_ride for user_ride in user.rides if ride_conflicts(ride, user_ride)]
    if conflicting_rides:
        logging.warning(f"User {user.username} has conflicting upcoming rides and cannot join ride {ride_id}")
        return jsonify({"message": "User has conflicting upcoming ride(s). Cannot join."}), 400

    ride.requesters.append(user)
    db.session.commit()

    logging.info(f"User {user.username} requested to join ride {ride_id} succesfully")
    return jsonify({"message": "User joined the ride successfully"}), 200

def ride_conflicts(ride1, ride2):
    logging.info(f"Checking for conflicts between {ride1.ride_id} and {ride2.ride_id}")
    return ride1.latest_pickup_time > ride2.earliest_pickup_time and ride2.latest_pickup_time > ride1.earliest_pickup_time

@app.route('/rides/<int:ride_id>/accept_requester/<int:requester_id>', methods=['POST'])
def accept_requester(ride_id, requester_id): # requester_id is user_id of requester
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    current_user_id = user.user_id
    ride = Ride.query.get_or_404(ride_id)

    logging.info(f"User {current_user_id} attempting to accept requester {requester_id} for ride {ride_id}")

    if ride.creator_id != current_user_id:
        logging.warning(f"User {current_user_id} is not the creator of ride {ride_id}")
        return jsonify({"message": "Only the creator of the ride can accept requesters"}), 403

    requester = User.query.get_or_404(requester_id)

    if requester not in ride.requesters:
        logging.warning(f"User {requester_id} is not a requester of ride {ride_id}")
        return jsonify({"message": "User is not a requester of this ride"}), 400

    if len(ride.members) >= ride.max_group_size:
        logging.warning(f"Ride {ride_id} is full. Cannot accept more requesters")
        return jsonify({"message": "The ride is full"}), 400

    ride.requesters.remove(requester)
    ride.members.append(requester)
    db.session.commit()

    logging.info(f"User {requester_id} has been accepted to ride {ride_id} by user {current_user_id}")
    return jsonify({"message": "Requester accepted successfully"}), 200



@app.route('/rides/<int:ride_id>/leave', methods=['POST'])
def leave_ride(ride_id):
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    ride = Ride.query.get_or_404(ride_id)

    logging.info(f"User {user.username} attempting to leave ride {ride_id}")

    if user not in ride.members:
        logging.warning(f"User {user.username} is not a member of ride {ride_id}")
        return jsonify({"message": "User is not a member of this ride"}), 400

    if len(ride.members) == 1:
        db.session.delete(ride)
        db.session.commit()
        logging.info(f"User {user.username} left ride {ride_id} and the ride has been deleted")
        return jsonify({"message": "User left the ride successfully and the ride has been deleted"}), 200

    ride.members.remove(user)
    db.session.commit()
    logging.info(f"User {user.username} left ride {ride_id} successfully")
    return jsonify({"message": "User left the ride successfully"}), 200

@app.route('/rides/<int:ride_id>/cancel_request', methods=['POST'])
def cancel_request(ride_id):
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    current_user_id = user.user_id
    ride = Ride.query.get_or_404(ride_id)

    logging.info(f"User {current_user_id} is attempting to cancel request for ride {ride_id}")

    if user not in ride.requesters:
        logging.warning(f"User {current_user_id} has not requested to join ride {ride_id}")
        return jsonify({"message": "User has not requested to join this ride"}), 400

    ride.requesters.remove(user)
    db.session.commit()

    logging.info(f"User {current_user_id} has successfully cancelled request to join ride {ride_id}")
    return jsonify({"message": "Request cancelled successfully"}), 200

@app.route('/rides/<int:ride_id>/members', methods=['GET'])
def get_ride_members(ride_id):
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    logging.info(f"User {user.username} attempting to get members of ride {ride_id}")

    ride = Ride.query.get_or_404(ride_id)
    members = ride.members

    logging.info(f"User {user.username} successfully retrieved members of ride {ride_id}")
    return jsonify([member.to_json() for member in members]), 200

@app.route('/rides/<int:ride_id>/requesters', methods=['GET'])
def get_ride_requesters(ride_id): 
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    logging.info(f"User {user.user_id} attempting to get members of ride {ride_id}")

    ride = Ride.query.get_or_404(ride_id)
    requesters = ride.requesters

    if ride.creator_id != user.user_id:
        logging.warning(f"User {user.user_id} does not have permission to update ride {ride_id}")
        return jsonify({"message": "Permission denied"}), 403

    logging.info(f"User {user.user_id} successfully retrieved members of ride {ride_id}")
    return jsonify([requester.to_json() for requester in requesters]), 200

@app.route('/users/rides', methods=['GET', 'POST'])
def get_user_rides():
    print("get user rides request received. ")
    print(request.headers)
    print(check_authentication(request))
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    data = request.json
    ride_type = data.get('time', 'all')  # Get the type parameter from the request, default to 'all'  
    logging.info(f"Fetching data for user {user.username}") 

    # THIS LINE IS UNECESSARY (AND BUGGY) AS WE ALREADY GET THE USER USING THE AUTHENTICATION TOKEN.
    # user = User.query.get_or_404(user.username) 
    created_rides = user.created_rides
    member_rides = user.rides
    requested_rides = user.requested_rides

    logging.info(f"User {user.username} data retrieved. Filtering rides by type: {ride_type}")

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
    filtered_requested_rides = filter_rides(requested_rides, ride_type)

    logging.info(f"Rides filtered  for user {user.username}: {len(filtered_created_rides)} created, {len(filtered_member_rides)} joined")

    return jsonify({
        "created_rides": [ride.to_json() for ride in filtered_created_rides],
        "member_rides": [ride.to_json() for ride in filtered_member_rides],
        "requested_rides": [ride.to_json() for ride in filtered_requested_rides]
    }), 200

@app.route('/users/upcoming_rides', methods=['GET'])
def get_user_upcoming_rides():
    try:
        user = check_authentication(request)
    except Unauthorized as e:
        return jsonify({"message": e.args[0]})

    logging.info(f"Fetching upcoming rides for user {user.username}")
    user = User.query.get_or_404(user.username)
    upcoming_rides = [ride for ride in user.rides if ride.latest_pickup_time > datetime.now()]

    logging.info(f"Upcoming rides filtered for user {user.username}")
    return jsonify([ride.to_json() for ride in upcoming_rides]), 200

if __name__ == "__main__":
    port = 5000
    app.run(debug=True, host='0.0.0.0')

