from __main__ import app
from flask import request, jsonify

import logging 
from models import Ride
from config import db

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
