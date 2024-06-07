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
    
    data = request.json
    desired_pickup_latitude = float(data.get('desiredPickupLatitude'))
    desired_pickup_longitude = float(data.get('desiredPickupLongitude'))
    desired_destination_latitude = float(data.get('desiredDestinationLatitude'))
    desired_destination_longitude = float(data.get('desiredDestinationLongitude'))
    min_date = data.get('minDate', datetime.datetime.now())
    max_date = data.get('maxDate', datetime.datetime.max)
    pickup_radius_threshold = data.get('pickupRadiusThreshold', float('inf'))
    dropoff_radius_threshold = data.get('dropoffRadiusThreshold', float('inf'))
    sort_by = data.get('sortBy', None)

    
    if not desired_destination_latitude or not desired_destination_longitude:
        return jsonify({"error": "Missing desired destination location"}), 400

    # FIX THIS START
    subquery = (
        db.session.query(Ride.ride_id, func.count(Ride.members).label('member_count'))
        .group_by(Ride.ride_id)
        .subquery()
    )
    RideAlias = aliased(Ride, subquery)
    
    rides = db.session.query(Ride).join(
        subquery, Ride.ride_id == subquery.c.ride_id
    ).filter(
        (Ride.earliest_pickup_time >= min_date) &
        (Ride.latest_pickup_time <= max_date) &
        (Ride.creator_id != user.user_id) &
        (subquery.c.member_count < Ride.max_group_size)
    ).all()
    # FIX THIS END

    logging.info(f"Retrieved {len(rides)} rides from the database")

    print(type(desired_pickup_latitude), desired_pickup_latitude)
    print(type(desired_pickup_longitude), desired_pickup_longitude)
    print(type(desired_destination_latitude), desired_destination_latitude)
    print(type(desired_destination_longitude), desired_destination_longitude)

    # filter by radii
    filtered_rides = [
        ride for ride in rides
        if distance((desired_pickup_latitude, desired_pickup_longitude),
                    (ride.pickup_latitude, ride.pickup_longitude)).miles <= int(pickup_radius_threshold) and
           distance((desired_destination_latitude, desired_destination_longitude),
                    (ride.destination_latitude, ride.destination_longitude)).miles <= int(dropoff_radius_threshold)
    ]

    logging.info(f"Filtered down to {len(filtered_rides)} rides based on radius thresholds")

    # sort filtered rides by key
    if sort_by == 'pickup_location':
        sorted_rides = sorted(filtered_rides, key=lambda ride: distance((desired_pickup_latitude, desired_pickup_longitude),
                                                                        (ride.pickup_latitude, ride.pickup_longitude)).miles)
    elif sort_by == 'destination_location':
        sorted_rides = sorted(filtered_rides, key=lambda ride: distance((desired_destination_latitude, desired_destination_longitude),
                                                                        (ride.destination_latitude, ride.destination_longitude)).miles)
    elif sort_by == 'pickup_time':
        sorted_rides = sorted(filtered_rides, key=lambda ride: ride.earliest_pickup_time)
    else: # no valid sorting key provided
        sorted_rides = filtered_rides

    logging.info(f"Returning {len(sorted_rides)} sorted rides")

    return jsonify([ride.to_json() for ride in sorted_rides])