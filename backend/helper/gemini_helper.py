from config import db
from models import User, Ride
import google.generativeai as genai
from flask import request
from geopy.distance import geodesic
from collections import Counter

from .geolocation import get_location


genai.configure(api_key = 'AIzaSyCYNiJhJpxL8Oth-JnVvBAqBhDGNE8lHeI')
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def get_user_count():
    try:
        user_count = User.query.count()
        return user_count
    except Exception as e:
        print(f"Error while rerieving user count: {str(e)}")
        return None
    
def get_ride_count():
    try:
        ride_count = Ride.query.count()
        return ride_count
    except Exception as e:
        print(f"Error while rerieving user count: {str(e)}")
        return None

def get_last_created_ride():
    last_ride = Ride.query.order_by(Ride.earliest_pickup_time.desc()).first()
    output = f"{last_ride} at {last_ride.earliest_pickup_time} with description: {last_ride.description}"
    return output

def get_closest_ride():
    all_rides = Ride.query.all()
    closest_ride = None
    min_distance = float('inf')
    lat_lng = get_location()
    latitude = lat_lng['location']['lat']
    longitude = lat_lng['location']['lng']

    for ride in all_rides:
        ride_location = (ride.pickup_latitude, ride.pickup_longitude)
        user_location = (latitude, longitude)
        distance = geodesic (user_location, ride_location).miles
        if distance < min_distance:
            min_distance = distance
            closest_ride = ride

    return closest_ride.description

def get_busiest_day():
    rides = Ride.query.all()
    weekdays = [ride.earliest_pickup_time.weekday() for ride in rides]

    weekday_counter = Counter(weekdays)
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    busiest_day_index = weekday_counter.most_common(1)[0][0]
    busiest_day_name = weekday_names[busiest_day_index]

    return busiest_day_name

PRESET_RESPONSES = [
    f"We currently have {str(get_user_count())} users",
    f"We have {str(get_ride_count())} rides available",
    f"The last ride created was {str(get_last_created_ride())}",
    f"The closest ride to you is {str(get_closest_ride())}",
    f"The busiest day is {str(get_busiest_day())}",
    f"Sorry, I do not know"
]

def query_gemini_ai(query):
    prompt = f"You are a very simple help chat assistant\n"
    prompt += f"This user asked you this: '''{query}'''\n"
    prompt += f"If the user exactly asks 'Tell me about the Navier-Stokes Equations', respond with information about the equations"
    prompt += f"Otherwise, you choose between these six present responses to answer with '''{','.join(PRESET_RESPONSES)}'''\n"
    response = model.generate_content(prompt)
    content_parts = response._result.candidates[0].content.parts
    text_content = [part.text for part in content_parts]
    
    return text_content









