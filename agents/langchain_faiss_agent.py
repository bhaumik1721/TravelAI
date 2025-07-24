# agents/langchain_faiss_agent.py

from agents.langchain_gemini_agent import generate_with_langchain
from memory.faiss_memory import (
    load_or_create_vectorstore,
    store_response,
    check_for_similar_response
)
from utils.google_services import fetch_full_city_info

def process_travel_query(city, query, interests, duration, start_date=None):
    try:
        user_query = f"{duration}-day trip to {city} for {interests} on {start_date}"
        vectorstore = load_or_create_vectorstore()
        cached = check_for_similar_response(user_query, vectorstore)

        if cached:
            print("📦 Retrieved from FAISS memory:")
            return cached

        # 🚨 Fetch and check city data
        city_data = fetch_full_city_info(city, query, duration, start_date)
        print("📊 city_data received:", city_data)

        if not city_data or "places" not in city_data:
            return "❌ Could not fetch places or weather for this city."

        weather_list = city_data.get("weather", [])
        places_list = city_data.get("places", [])

        # ✅ Safe weather string
        if weather_list:
            weather_str = "\n".join(
                [f"{w.get('datetime', '')}: {w.get('condition', '')}, {w.get('temp', '')}°C — {w.get('tip', '')}" for w in weather_list]
            )
        else:
            weather_str = "Weather data not available."

        # ✅ Safe places string
        if places_list:
            places_str = "\n".join(
                [f"{p.get('name', '')} - {p.get('vicinity', p.get('formatted_address', 'No address'))}" for p in places_list]
            )
        else:
            places_str = "No places of interest found."

        print("✅ Final weather_str:", weather_str)
        print("✅ Final places_str:", places_str)
        print("✅ Final prompt being sent to Gemini...")

        # 🔮 Generate final response
        response = generate_with_langchain(
            city=city,
            interests=interests,
            weather=weather_str,
            places=places_str,
            duration=duration
        )

        # 🧠 Save in FAISS
        store_response(user_query, response, vectorstore)
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()  # print full error in console
        return f"❌ Error occurred: {str(e)}"




