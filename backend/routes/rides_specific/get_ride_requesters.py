from __main__ import app
from flask import request, jsonify

import logging
from models import Ride

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

