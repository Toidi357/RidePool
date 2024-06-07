from __main__ import app
from flask import request, jsonify

import logging
from models import Ride

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
