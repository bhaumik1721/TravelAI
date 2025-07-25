# agents/langchain_faiss_agent.py
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.google_places import get_places_by_city
from utils.google_services import fetch_full_city_info
from utils.date_utils import get_forecast_dates
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from memory.chroma_memory import retrieve_similar_context, add_to_chroma_memory

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

# 🧠 Prompt
prompt = ChatPromptTemplate.from_template("""
You are a helpful travel assistant. Based on the following inputs, generate a personalized itinerary.

City: {city}
User Interests: {interests}
Trip Duration (days): {duration}
Top Searched Places: {places}

Also consider this user's previous preferences:
{past_memory}

Output a detailed, conversational and fun itinerary.
""")

# 🛠️ Chain
def process_travel_query(city: str, query: str, interests: str, duration: int, places: str) -> str:
    from langchain_core.runnables import RunnableMap, RunnablePassthrough

    user_query = f"{city} trip for {duration} days focused on {interests}"

    # Try to retrieve similar memory
    memory_context = retrieve_similar_context(user_query)

    chain = (
        RunnableMap({
            "city": RunnablePassthrough(),
            "query": RunnablePassthrough(),
            "interests": RunnablePassthrough(),
            "duration": RunnablePassthrough(),
            "places": RunnablePassthrough(),
            "past_memory": lambda x: memory_context or "No prior trips."
        })
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke({
        "city": city,
        "query": query,
        "interests": interests,
        "duration": duration,
        "places": places
    })

    # Save interaction to memory
    add_to_chroma_memory(user_query, response)

    return response
