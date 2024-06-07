from __main__ import app
from flask import request, jsonify

import logging
import datetime
from sqlalchemy import func
from sqlalchemy.orm import aliased
from geopy.distance import distance
from models import Ride
from config import db

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
    min_date = data.get('minDate')
    max_date = data.get('maxDate')
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
        if compare_dates(ride.earliest_pickup_time.isoformat(), min_date) and
        compare_dates(max_date, ride.latest_pickup_time.isoformat()) and
        ride.creator_id != user.user_id and
        len(ride.members) < ride.max_group_size
    ]

    # Additional radius filtering in Python (optional based on your use case)
    def within_threshold(lat1, lon1, lat2, lon2, threshold):
        # Using a simplified distance formula (not accurate for long distances or near poles)
        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 <= threshold

    if float(pickup_radius_threshold) < float('inf'):
        filtered_rides = [
            ride for ride in filtered_rides
            if within_threshold(ride.pickup_latitude, ride.pickup_longitude, desired_pickup_latitude, desired_pickup_longitude, pickup_radius_threshold)
        ]

    if float(dropoff_radius_threshold) < float('inf'):
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