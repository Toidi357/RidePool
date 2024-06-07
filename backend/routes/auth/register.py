from flask import request, jsonify
from __main__ import app

import logging 
from config import bcrypt, db
from models import User

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    logging.info(f"Received registration request: {data}")

    required_fields = ['username', 'password', 'firstName', 'lastName', 'email', 'phoneNumber']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # check if user already exists
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({"error": f"User already exists. Please log in."}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        phone_number=data['phoneNumber']
    )
    db.session.add(new_user)
    db.session.commit()
    logging.info(f"User registered succesfully: {new_user.username}")
    auth_token = new_user.encode_auth_token(new_user.username)
    return jsonify({"message": "User registered successfully", "auth_token": auth_token}), 201