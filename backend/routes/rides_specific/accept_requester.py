from __main__ import app
from flask import request, jsonify

import logging 
from models import Ride, User
from config import db

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

