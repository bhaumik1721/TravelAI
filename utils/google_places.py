# utils/google_places.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def get_coordinates(city_name):
    """Get latitude and longitude from city name using Geocoding API"""
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city_name, "key": GOOGLE_PLACES_API_KEY}
    res = requests.get(geocode_url, params=params).json()

    if res["status"] == "OK" and res["results"]:
        loc = res["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]

    raise Exception(f"[ERROR] Geocoding failed for '{city_name}' - {res.get('status')} - {res.get('error_message', '')}")


def search_places_nearby(lat, lng, keyword="tourist attraction", radius=10000, type_filter=None):
    """Search for nearby places using Places API"""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": keyword,
        "key": GOOGLE_PLACES_API_KEY
    }
    if type_filter:
        params["type"] = type_filter

    res = requests.get(url, params=params).json()

    if res["status"] == "OK":
        return res.get("results", [])
    else:
        raise Exception(f"[ERROR] Places API failed - {res.get('status')} - {res.get('error_message', '')}")


def get_place_details(place_id):
    """Get full details of a place (e.g. photos, opening hours)"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_address,opening_hours,photos,geometry",
        "key": GOOGLE_PLACES_API_KEY
    }
    res = requests.get(url, params=params).json()

    if res["status"] == "OK":
        return res.get("result", {})
    else:
        raise Exception(f"[ERROR] Place details fetch failed - {res.get('status')} - {res.get('error_message', '')}")


def get_places_by_city(city_name, keyword="tourist attraction", radius=10000, type_filter=None):
    """Full flow: City → coordinates → top 5 nearby places with details"""
    lat, lng = get_coordinates(city_name)
    nearby = search_places_nearby(lat, lng, keyword, radius, type_filter)

    places = []
    for place in nearby[:5]:  # Limit to top 5 to save on API calls
        place_id = place.get("place_id")
        if not place_id:
            continue
        try:
            full_details = get_place_details(place_id)
            places.append(full_details)
        except Exception as e:
            print(f"[WARN] Skipping place due to error: {e}")

    return places
