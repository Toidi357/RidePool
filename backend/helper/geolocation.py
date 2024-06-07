import requests

def get_location():
    ip_address = requests.get('http://api.ipify.org').text
    response = requests.get(f"http://ip-api.com/json/{ip_address}").json()
    latitude = response['lat']
    longitude = response['lon']
    location_data = {"location": {"lat": latitude, "lng": longitude}}
    return location_data


