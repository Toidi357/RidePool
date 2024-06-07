from __main__ import app
from flask import request, jsonify

import logging

@app.route('/profile', methods=['GET'])
def get_user_profile():
    logging.info("GET /profile hit")
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401
    
    responseObject = {
        "userId": user.user_id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
        'average_rating':user.avg_rating,
    }
    return jsonify(responseObject), 200