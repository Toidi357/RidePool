from __main__ import app
from flask import request, jsonify

import logging
from dateutil import parser
from models import Ride
from config import db

@app.route('/rides', methods=['POST'])
def create_ride():
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    data = request.json

    logging.info(f"User {user.username} is attempting to create a new ride")

    logging.info (f"Received data for ride creation: {data}")

    required_fields = ['pickupLongitude', 'pickupLatitude', 'destinationLongitude', 'destinationLatitude', 'pickupThreshold', 'destinationThreshold', 'earliestPickupTime', 'latestPickupTime', 'maxGroupSize', 'description'] # , 'preferredApps'

    for field in required_fields:
        if field not in data:
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

    new_ride.creator.append(user)
    new_ride.members.append(user)


    db.session.add(new_ride)
    db.session.commit()

    logging.info (f"New ride created succesfully: {new_ride.to_json()}")
    return jsonify(new_ride.to_json()), 201