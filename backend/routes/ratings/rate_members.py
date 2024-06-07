from __main__ import app
from flask import request, jsonify

import logging
from models import Ride, User
from config import db

@app.route('/rides/<int:ride_id>/rate_members', methods=['POST'])
def rate_members(ride_id):
    logging.info(f'Attempting to rate ride {ride_id}')
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    ride = Ride.query.get_or_404(ride_id)
    data = request.json

    if user not in ride.members:
        return jsonify({"message": "You are not a member of this ride"}), 403

    for member_id, rating in data.items():
        if not (1 <= int(rating) <= 5):
            return jsonify({"message": "Rating must be between 1 and 5"}), 400
        member = User.query.get(member_id)

        if not member or member == user:
            return jsonify({"message": "Invalid member ID or you cannot rate yourself"}), 400
        
        member.rating_sum += rating
        member.num_ratings += 1
        member.avg_rating = member.rating_sum / member.num_ratings

        db.session.commit()

    return jsonify({"message": "Ratings submitted successfully"}), 200
