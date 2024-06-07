from __main__ import app
from flask import request, jsonify

import logging 
import datetime
from models import Ride
from config import db

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
    ride.earliest_pickup_time = datetime.datetime.fromisoformat(data.get('earliestArrivalTime', ride.earliest_pickup_time.isoformat()))
    ride.latest_pickup_time = datetime.datetime.fromisoformat(data.get('latestArrivalTime', ride.latest_pickup_time.isoformat()))
    ride.max_group_size = data.get('maxGroupSize', ride.max_group_size)
    ride.description = data.get('description', ride.description)
    # ride.preferred_apps = data.get('preferredApps', ride.preferred_apps)
    db.session.commit()
    logging.info(f"Ride {ride_id} updated succesfully")
    return jsonify(ride.to_json())
