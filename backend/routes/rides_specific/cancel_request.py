from __main__ import app
from flask import request, jsonify

import logging
from models import Ride
from config import db

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
