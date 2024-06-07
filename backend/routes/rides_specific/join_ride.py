from __main__ import app
from flask import request, jsonify

import logging 
from models import Ride
from config import db

def ride_conflicts(ride1, ride2):
    logging.info(f"Checking for conflicts between {ride1.ride_id} and {ride2.ride_id}")
    return ride1.latest_pickup_time > ride2.earliest_pickup_time and ride2.latest_pickup_time > ride1.earliest_pickup_time

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