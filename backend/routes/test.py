from flask import request, jsonify
from __main__ import app

@app.route('/test', methods = ['GET']) 
def test():
    return jsonify({'response': 'connection successful'})