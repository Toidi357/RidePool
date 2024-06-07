from flask import request, jsonify
from config import app, db
from models import User, Ride
from datetime import datetime
import logging

from datetime import datetime

from flask_migrate import Migrate

from routes import test, gemini_query
from routes.auth import login, register, logout, refresh_token
from routes.profile import get_user_profile, update_user_profile
from routes.users import get_user_rides, get_user_upcoming_rides
from routes.rides_general import create_ride, get_rides

migrate = Migrate(app, db)


logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')

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
app.config.Unauthorized = Unauthorized
app.config.check_authentication = check_authentication

@app.route('/rides/<int:ride_id>', methods=['PUT'])
def update_ride(ride_id):
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

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
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    current_user_id = user.user_id
    logging.info(f"User {current_user_id} is attempting to join ride {ride_id}")
    ride = Ride.query.get_or_404(ride_id)
    logging.info(f"Ride {ride_id} retrieved from the database")
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
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

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
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

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
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

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
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    logging.info(f"User {user.username} attempting to get members of ride {ride_id}")

    ride = Ride.query.get_or_404(ride_id)
    members = ride.members

    logging.info(f"User {user.username} successfully retrieved members of ride {ride_id}")
    return jsonify([member.to_json() for member in members]), 200

@app.route('/rides/<int:ride_id>/requesters', methods=['GET'])
def get_ride_requesters(ride_id): 
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    logging.info(f"User {user.user_id} attempting to get members of ride {ride_id}")

    ride = Ride.query.get_or_404(ride_id)
    requesters = ride.requesters

    if ride.creator_id != user.user_id:
        logging.warning(f"User {user.user_id} does not have permission to update ride {ride_id}")
        return jsonify({"message": "Permission denied"}), 403

    logging.info(f"User {user.user_id} successfully retrieved members of ride {ride_id}")
    return jsonify([requester.to_json() for requester in requesters]), 200



@app.route('/rides/<int:ride_id>/rate_members', methods=['POST'])
def rate_members(ride_id):
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    ride = Ride.query.get_or_404(ride_id)
    data = request.json

    if user not in ride.members:
        return jsonify({"message": "You are not a member of this ride"}), 403

    for member_id, rating in data.items():
        if not (1 <= int(rating) <= 5):
            return jsonify({"message": "Rating must be between 1 and 5"}), 400
        member = User.query.get(member_id)

        if not member or member == user:
            return jsonify({"message": "Invalid member ID or you cannot rate yourself"}), 400
        
        member.rating_sum += rating
        member.num_ratings += 1
        member.avg_rating = member.rating_sum / member.num_ratings

        db.session.commit()

    return jsonify({"message": "Ratings submitted successfully"}), 200

@app.route('/rides/<int:ride_id>/members_to_rate', methods=['GET'])
def get_ride_members_to_rate(ride_id):
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    logging.info(f"User {user.username} attempting to get members of ride {ride_id}")

    ride = Ride.query.get_or_404(ride_id)
    members = ride.members

    logging.info(f"User {user.username} successfully retrieved members of ride {ride_id}")
    return jsonify([member.to_json() for member in members if member.user_id != user.user_id]), 200

@app.route('/rides/active/<int:ride_id>', methods=['GET'])
def get_ride_status(ride_list=None, ride_id=None):
    try:
        user = app.config.check_authentication(request)  
    except app.config.Unauthorized as e:
        return jsonify({"message": str(e)}), 401
    
    ride = Ride.query.get_or_404(ride_id)
    now = datetime.now()

    if ride.latest_pickup_time > now:
        return jsonify({"ride_status": "active"}), 200
    else:
        return jsonify({"ride_status": "history"}), 200


if __name__ == "__main__":
    port = 5000
    app.run(debug=True, host='0.0.0.0')

