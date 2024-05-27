import requests

def get_location():
    response = requests.post('https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyB0c2L4gDETEWEgCfTjRXxCtyLYyiFAHTg', json={'considerIp': 'true'})
    location_data = response.json()
    return location_data


