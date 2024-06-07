from __main__ import app
from flask import request, jsonify

import logging
import datetime

@app.route('/users/rides', methods=['GET', 'POST'])
def get_user_rides():
    logging.info("get user rides request received. ")
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    data = request.json
    ride_type = data.get('time', 'all')  # Get the type parameter from the request, default to 'all'  
    logging.info(f"Fetching data for user {user.username}") 

    created_rides = user.created_rides
    member_rides = user.rides
    requested_rides = user.requested_rides

    logging.info(f"User {user.username} data retrieved. Filtering rides by type: {ride_type}")

    now = datetime.datetime.now()

    def filter_rides(rides, ride_type):
        if ride_type == 'current':
            return [ride for ride in rides if ride.latest_pickup_time > now]
        elif ride_type == 'history':
            return [ride for ride in rides if ride.latest_pickup_time <= now]
        else:  # 'all'
            return rides

    filtered_created_rides = filter_rides(created_rides, ride_type)
    filtered_member_rides = filter_rides(member_rides, ride_type)
    filtered_requested_rides = filter_rides(requested_rides, ride_type)

    logging.info(f"Rides filtered  for user {user.username}: {len(filtered_created_rides)} created, {len(filtered_member_rides)} joined")

    return jsonify({
        "created_rides": [ride.to_json() for ride in filtered_created_rides],
        "member_rides": [ride.to_json() for ride in filtered_member_rides],
        "requested_rides": [ride.to_json() for ride in filtered_requested_rides]
    }), 200