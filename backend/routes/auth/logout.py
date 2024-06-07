from flask import request, jsonify
from __main__ import app

import logging 
from models import User, BlacklistToken
from config import db

@app.route('/logout', methods=['GET'])
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    'message': 'Logout successful'
                }
                return jsonify(responseObject), 200
            except Exception as e:
                return jsonify({'message': 'Error'}), 500
            
    logging.info("User logged out succesfully")
    return jsonify({"message": "Unauthorized"}), 401