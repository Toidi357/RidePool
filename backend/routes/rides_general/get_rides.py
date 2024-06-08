from __main__ import app
from flask import request, jsonify

import logging
import datetime
from sqlalchemy import func
from sqlalchemy.orm import aliased
from geopy.distance import distance
from models import Ride
from config import db

from datetime import datetime

@app.route('/rides/search', methods=['POST'])
def get_rides():
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401
    from dateutil import parser

    data = request.json
    desired_pickup_latitude = float(data.get('desiredPickupLatitude'))
    desired_pickup_longitude = float(data.get('desiredPickupLongitude'))
    desired_destination_latitude = float(data.get('desiredDestinationLatitude'))
    desired_destination_longitude = float(data.get('desiredDestinationLongitude'))
    iso_string = data.get('minDate')
    min_date = datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S.%fZ') if 'Z' in iso_string else datetime.fromisoformat(iso_string)
    iso_string = data.get('maxDate')
    max_date = datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S.%fZ') if 'Z' in iso_string else datetime.fromisoformat(iso_string)
    pickup_radius_threshold = float(data.get('pickupRadiusThreshold', float('inf')))
    dropoff_radius_threshold = float(data.get('dropoffRadiusThreshold', float('inf')))
    sort_by = data.get('sortBy', None)

    
    if not desired_destination_latitude or not desired_destination_longitude:
        return jsonify({"error": "Missing desired destination location"}), 400

    # FIX THIS START
    # FIX THIS END

    # logging.info(f"Retrieved {len(rides)} rides from the database")

    # print(type(desired_pickup_latitude), desired_pickup_latitude)
    # print(type(desired_pickup_longitude), desired_pickup_longitude)
    # print(type(desired_destination_latitude), desired_destination_latitude)
    # print(type(desired_destination_longitude), desired_destination_longitude)

    # # filter by radii
    # filtered_rides = [
    #     ride for ride in rides
    #     if distance((desired_pickup_latitude, desired_pickup_longitude),
    #                 (ride.pickup_latitude, ride.pickup_longitude)).miles <= int(pickup_radius_threshold) and
    #        distance((desired_destination_latitude, desired_destination_longitude),
    #                 (ride.destination_latitude, ride.destination_longitude)).miles <= int(dropoff_radius_threshold)
    # ]

    # Fetch all rides and filter using Python
    # Custom string date comparison function
    def compare_dates(date_str1, date_str2):
        return date_str1 >= date_str2

    # Fetch all rides and filter using Python
    all_rides = db.session.query(Ride).all()

    # Filter based on the criteria
    filtered_rides = [
        ride for ride in all_rides
        if compare_dates(ride.earliest_pickup_time, min_date) and
        compare_dates(max_date, ride.latest_pickup_time) and
        ride.creator_id != user.user_id and
        len(ride.members) < ride.max_group_size
    ]
    print("before distance filter")
    print(filtered_rides)

    # Additional radius filtering in Python
    def within_threshold(lat1, lon1, lat2, lon2, threshold):
        # Using a simplified distance formula
        import math
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) <= threshold

    # Ensure thresholds are floats
    pickup_radius_threshold = float(pickup_radius_threshold)
    dropoff_radius_threshold = float(dropoff_radius_threshold)

    # Desired locations for pickup and dropoff
    desired_pickup_latitude = float(desired_pickup_latitude)
    desired_pickup_longitude = float(desired_pickup_longitude)
    desired_destination_latitude = float(desired_destination_latitude)
    desired_destination_longitude = float(desired_destination_longitude)

    

    # Filter rides based on pickup radius threshold
    if pickup_radius_threshold < float('inf'):
        filtered_rides = [
            ride for ride in filtered_rides
            if within_threshold(ride.pickup_latitude, ride.pickup_longitude, desired_pickup_latitude, desired_pickup_longitude, pickup_radius_threshold)
        ]

    # Filter rides based on dropoff radius threshold
    if dropoff_radius_threshold < float('inf'):
        filtered_rides = [
            ride for ride in filtered_rides
            if within_threshold(ride.destination_latitude, ride.destination_longitude, desired_destination_latitude, desired_destination_longitude, dropoff_radius_threshold)
        ]




    logging.info(f"Filtered down to {len(filtered_rides)} rides based on radius thresholds")
    sorted_rides = filtered_rides
    # sort filtered rides by key
    # if sort_by == 'pickup_location':
    #     sorted_rides = sorted(filtered_rides, key=lambda ride: distance((desired_pickup_latitude, desired_pickup_longitude),
    #                                                                     (ride.pickup_latitude, ride.pickup_longitude)).miles)
    # elif sort_by == 'destination_location':
    #     sorted_rides = sorted(filtered_rides, key=lambda ride: distance((desired_destination_latitude, desired_destination_longitude),
    #                                                                     (ride.destination_latitude, ride.destination_longitude)).miles)
    # elif sort_by == 'pickup_time':
    #     sorted_rides = sorted(filtered_rides, key=lambda ride: ride.earliest_pickup_time)
    # else: # no valid sorting key provided
    #     sorted_rides = filtered_rides

    logging.info(f"Returning {len(sorted_rides)} sorted rides")

    return jsonify([ride.to_json() for ride in sorted_rides])