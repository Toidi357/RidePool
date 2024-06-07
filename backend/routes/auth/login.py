from flask import request, jsonify
from __main__ import app

import logging 
from config import bcrypt
from models import User

from helper.geolocation import get_location

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    logging.info(f"Received login request data: {data}")

    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Both username and password are required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        auth_token = user.encode_auth_token(user.username)
        
        if auth_token:
            responseObject = {
                'message': 'Successfully logged in.',
                'auth_token': auth_token,
            }
            # Capture the location
            location_data = get_location()
            user.latitude = location_data['location']['lat']
            
            user.longitude = location_data['location']['lng']

            return jsonify(responseObject), 200
        
        logging.info(f"User {user.username} logged in succesfully")
        return jsonify({"message": "Login successful"}), 200
    
    logging.warning("Invalid login credentials")
    return jsonify({"message": "Invalid credentials"}), 401