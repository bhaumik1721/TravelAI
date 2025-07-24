# google_services.py
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Load your API key from environment variables or securely from a config file
GOOGLE_PLACES_API_KEY =  os.getenv("GOOGLE_PLACES_API_KEY")
OPEN_WEATHER_API_KEY  =  os.getenv("OPEN_WEATHER_API_KEY")

# 1. Get Coordinates from City Name (Geocoding API)
def get_coordinates(city_name):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city_name, "key": GOOGLE_PLACES_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK' and data['results']: # Add this check
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        # Improved error handling to provide more specific feedback
        error_message = data.get('error_message', 'No results found or API error.')
        print(f"[ERROR] Geocoding error for {city_name}: {error_message}")
        return None, None



# 2. Search Places (Nearby Search API)
def search_places(query, lat, lng, radius=5000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": query,
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])

# 3. Get Place Details (Place Details API)
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_address,opening_hours,geometry,photos",
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get("result", {})

# 4. Get Weather Info (Google Weather API or fallback to OpenWeatherMap/other if needed)
def get_weather(lat, lng, target_dates=None):
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lng,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "metric"
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        raise Exception(f"Weather API error: {res.text}")

    data = res.json()
    forecasts = data.get("list", [])
    simplified = []

    if target_dates:
        target_dates = set(str(d) for d in target_dates)

    for forecast in forecasts:
        dt = datetime.fromtimestamp(forecast["dt"])
        if not target_dates or str(dt.date()) in target_dates:
            condition = forecast["weather"][0]["description"]
            temp = forecast["main"]["temp"]
            tip = generate_tip(condition, temp)

            simplified.append({
                "datetime": dt.strftime("%Y-%m-%d %H:%M"),
                "temp": temp,
                "condition": condition,
                "tip": tip
            })

    return simplified


def generate_tip(condition, temp):
    condition = condition.lower()
    if "rain" in condition:
        return "Don't forget your umbrella! ☔"
    elif "clear" in condition:
        return "Pack your sunglasses and sunscreen! 😎"
    elif "cloud" in condition:
        return "Looks cloudy — great day for sightseeing 🌥️"
    elif temp > 35:
        return "It's going to be hot — stay hydrated! 🥤"
    elif temp < 10:
        return "Chilly weather! Bring a jacket 🧥"
    else:
        return "Looks like a pleasant day. Enjoy! 😊"

# 5. Convenience Wrapper to Get All in One Shot
# ✅ PATCHED google_services.py

def fetch_full_city_info(city, query, start_date=None, duration_days=3):
    from utils.date_utils import get_forecast_dates

    lat, lng = get_coordinates(city)
    print(f"[INFO] Coordinates for {city}: {lat}, {lng}")

    if not lat:
        return {"places": [], "weather": []}

    places = search_places(query, lat, lng)
    print(f"[INFO] Found {len(places)} places for query '{query}'")

    detailed_places = []
    for p in places[:5]:
        try:
            print(f"🔍 Getting details for: {p.get('name', 'Unnamed')}")
            place_id = p.get("place_id")
            if not place_id:
                continue
            place_details = get_place_details(place_id)
            detailed_places.append(place_details)
        except Exception as e:
            print(f"⚠️ Skipping place due to error: {e}")
            continue

    return {
        "coordinates": {"lat": lat, "lng": lng},
        "places": detailed_places,
        "weather": []  # fully removed
    }





