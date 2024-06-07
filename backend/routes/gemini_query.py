from __main__ import app
from flask import request, jsonify

import logging 
from helper.gemini_helper import query_gemini_ai

@app.route('/gemini_query', methods = ['POST'])
def gemini_query():
    try:
        user = app.config.check_authentication(request)
    except app.config.Unauthorized as e:
        return jsonify({"message": e.args[0]}), 401
    

    data = request.json
    logging.info(f"User asked gemini: {data}")
    query = data.get('query')

    response = query_gemini_ai(query)
    logging.info(f"Gemini returned response: {response}")
    return jsonify({"response": response}), 200