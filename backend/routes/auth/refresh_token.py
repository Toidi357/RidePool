from __main__ import app
from flask import request, jsonify

import logging 
from models import BlacklistToken
from config import db

# aight we really getting into the weeds with this one
@app.route('/refresh_token', methods=['GET'])
def generate_refresh_token():
    logging.info("Refresh token endpoint hit")
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401

    try:
        # blacklist old token
        old_token = request.headers.get('Authorization').split(" ")[1]
        blacklist_token = BlacklistToken(token=old_token)
        # insert the token
        db.session.add(blacklist_token)
        db.session.commit()

        # create new one
        auth_token = user.encode_auth_token(user.username)
        return jsonify({"auth_token": auth_token}), 200
    except:
        return jsonify({"Internal Server Error"}), 500