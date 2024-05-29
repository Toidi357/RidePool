import requests

def get_location():
    # please replace this code with harsh's geolocation fix.
    # response = requests.post('https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyB0c2L4gDETEWEgCfTjRXxCtyLYyiFAHTg', json={'considerIp': 'true'})
    # location_data = response.json()
    location_data = {"location": {"lat": 0, "lng": 0}}
    return location_data


