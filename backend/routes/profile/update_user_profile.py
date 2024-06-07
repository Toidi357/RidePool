from __main__ import app
from flask import request, jsonify

import logging
from config import db

@app.route('/profile/update', methods=['POST'])
def update_user_profile():
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    data = request.json

    logging.info(f"User {user.username} is updating their profile")
    logging.info(f"Updated profile data received: {data}")
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.phone_number = data.get('phone_number', user.phone_number)

    db.session.commit()

    logging.info("User profile updated succesfully")

    return jsonify({"message": "User profile updated successfully"}), 200