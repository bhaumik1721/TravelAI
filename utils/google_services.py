# google_services.py
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Load your API key from environment variables or securely from a config file
GOOGLE_PLACES_API_KEY =  os.getenv("GOOGLE_PLACES_API_KEY")
OPEN_WEATHER_API_KEY  =  os.getenv("OPEN_WEATHER_API_KEY")
from utils.date_utils import get_forecast_dates


# 1. Geocoding API
def get_coordinates(city_name: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city_name, "key": GOOGLE_PLACES_API_KEY}
    response = requests.get(url, params=params).json()

    if response["status"] == "OK" and response["results"]:
        loc = response["results"][0]["geometry"]["location"]
        print(f"[INFO] Coordinates for {city_name}: {loc['lat']}, {loc['lng']}")
        return loc["lat"], loc["lng"]

    raise ValueError(f"[ERROR] Could not find coordinates for '{city_name}'")


# 2. Weather Info from OpenWeatherMap
def get_weather(lat: float, lon: float, target_dates=None):
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
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


# 3. Google Places Search
def search_places(query, lat, lng, radius=5000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": query,
        "key": GOOGLE_PLACES_API_KEY
    }
    res = requests.get(url, params=params)
    return res.json().get("results", [])


# 4. Google Place Details
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_address,opening_hours,geometry,photos",
        "key": GOOGLE_PLACES_API_KEY
    }
    res = requests.get(url, params=params)
    return res.json().get("result", {})


# 5. One-call Utility Function
def fetch_full_city_info(city, query, start_date=None, duration_days=3):
    lat, lng = get_coordinates(city)

    places_raw = search_places(query, lat, lng)
    print(f"[INFO] Found {len(places_raw)} places for query '{query}'")

    top_places = []
    for p in places_raw[:5]:
        try:
            place_id = p.get("place_id")
            print(f"🔍 Getting details for: {p.get('name', 'Unnamed')}")
            if place_id:
                top_places.append(get_place_details(place_id))
        except Exception as e:
            print(f"⚠️ Skipped: {e}")

    forecast_dates = get_forecast_dates(start_date, duration_days)
    weather = get_weather(lat, lng, forecast_dates)

    return {
        "coordinates": {"lat": lat, "lng": lng},
        "places": top_places,
        "weather": weather
    }





