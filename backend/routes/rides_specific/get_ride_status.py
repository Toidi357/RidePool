from __main__ import app
from flask import request, jsonify

import logging
import datetime
from models import Ride

@app.route('/rides/active/<int:ride_id>', methods=['GET'])
def get_ride_status(ride_list=None, ride_id=None):
    try:
        user = app.config.check_authentication(request)  
    except app.config.Unauthorized as e:
        return jsonify({"message": str(e)}), 401
    
    ride = Ride.query.get_or_404(ride_id)
    now = datetime.datetime.now()

    logging.info(f"Retrieving status of ride {ride_id}")

    if ride.latest_pickup_time > now:
        return jsonify({"ride_status": "active"}), 200
    else:
        return jsonify({"ride_status": "history"}), 200

