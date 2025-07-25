# agents/langchain_gemini_agent.py

import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.langchain_faiss_agent import GOOGLE_API_KEY

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # Use "gemini-1.5-pro" unless you're in Gemini Flash tier
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7,

)

prompt = PromptTemplate(
    input_variables=["city", "interests", "weather", "places", "duration"],
    template="""
You are a witty, helpful travel planner helping a user plan a {duration}-day trip to {city}.
They enjoy: {interests}

📍 Places of Interest:
{places}

🌦️ Weather Forecast:
{weather}

🎒 Based on the above, generate a full itinerary. Be conversational, clever, and fun! Include travel tips, local secrets, weather-based suggestions, and hidden gems.
"""
)

chain: Runnable = prompt | llm

def generate_with_langchain(city, interests, weather, places, duration):
    result = chain.invoke({
        "city": city,
        "interests": interests,
        "weather": weather,
        "places": places,
        "duration": duration

    })
    print("✅ Gemini output:", result)
    return result
