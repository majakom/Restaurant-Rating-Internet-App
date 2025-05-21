from geopy.geocoders import Nominatim
from time import sleep

def geocode_address(address):
    geolocator = Nominatim(user_agent="restaurant_app")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except:
        return None, None
