from config import app, db
from models import User
import logging

from flask_migrate import Migrate

from routes import test, gemini_query
from routes.auth import login, register, logout, refresh_token
from routes.profile import get_user_profile, update_user_profile
from routes.users import get_user_rides, get_user_upcoming_rides
from routes.rides_general import create_ride, get_rides
from routes.rides_specific import accept_requester, cancel_request, get_ride_members, get_ride_requesters, get_ride_status, join_ride, leave_ride, update_ride
from routes.ratings import get_ride_members_to_rate, rate_members

migrate = Migrate(app, db)

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')

# This next class and function are pushed to global variable to be used by each route
# These 2 declarations are in app.py not config b/c they rely on database models being imported
class Unauthorized(Exception):
    def __init__(self, message):
        super().__init__(message)
    
def check_authentication(request) -> User:
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            raise Unauthorized('Bearer token malformed.')
    else:
        auth_token = ''
    if auth_token: # means user *has* a token
        # resp should contain an object with the decoded token details
        # if its a string, that means its an error
        resp = User.decode_auth_token(auth_token)
        
        if not isinstance(resp, str):
            user = User.query.filter_by(username=resp['sub']).first()
            return user
        
        # special error message if token is expired
        if resp == 'Signature expired. Please log in again.':
            raise Unauthorized(resp)
    
    raise Unauthorized('Unauthorized')
app.config.Unauthorized = Unauthorized
app.config.check_authentication = check_authentication


if __name__ == "__main__":
    port = 5000
    app.run(debug=True, host='0.0.0.0')

