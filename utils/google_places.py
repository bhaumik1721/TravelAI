# utils/google_places.py

import os
import requests
from dotenv import load_dotenv

#from utils.google_services import GOOGLE_PLACES_API_KEY

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


def get_coordinates(city_name):
    """Get latitude and longitude from city name using Geocoding API"""
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": city_name,
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(geocode_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        raise Exception(f"Geocoding error: {data.get('status')} - {data.get('error_message', '')}")


def search_places_nearby(lat, lng, keyword="tourist attraction", radius=10000, type_filter=None):
    """Search for nearby places using Google Places Nearby Search API"""
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_PLACES_API_KEY,
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": keyword,
    }

    if type_filter:
        params["type"] = type_filter

    response = requests.get(places_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        return data["results"]
    else:
        raise Exception(f"Places API error: {data.get('status')} - {data.get('error_message', '')}")


def get_places_by_city(city_name, keyword="tourist attraction", radius=10000, type_filter=None):
    """Full flow: city name → coordinates → nearby places"""
    lat, lng = get_coordinates(city_name)
    return search_places_nearby(lat, lng, keyword, radius, type_filter)


# 🧪 Test it (optional)
'''if __name__ == "__main__":
    city = "Delhi"
    keyword = "club"  # try "restaurant", "cultural center", etc.

    try:
        places = get_places_by_city(city, keyword)
        for place in places[:5]:
            print(f"{place['name']} - {place.get('vicinity', 'No address')}")
    except Exception as e:
        print(f"Error: {e}")'''
