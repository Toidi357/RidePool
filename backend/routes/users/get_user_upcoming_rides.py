from __main__ import app
from flask import request, jsonify

import logging
import datetime

from models import User

@app.route('/users/upcoming_rides', methods=['GET'])
def get_user_upcoming_rides():
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    logging.info(f"Fetching upcoming rides for user {user.username}")
    user = User.query.get_or_404(user.username)
    upcoming_rides = [ride for ride in user.rides if ride.latest_pickup_time > datetime.datetime.now()]

    logging.info(f"Upcoming rides filtered for user {user.username}")
    return jsonify([ride.to_json() for ride in upcoming_rides]), 200