import sys
import os
from dotenv import load_dotenv


# Let Python find `agents`, `utils`, etc.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.langchain_faiss_agent import process_travel_query

load_dotenv()
import chainlit as cl

# chainlit_app/ui.py

@cl.on_message
async def handle_message(message: cl.Message):
    user_input = message.content.strip()
    await cl.Message(content="⏳ Planning your itinerary...").send()

    try:
        # Simple NLP fallback logic (you can enhance this later)
        if "trip" in user_input.lower() and "to" in user_input.lower():
            # Dummy fallback until you add parser
            city = "Mumbai"
            query = "tourist places"
            interests = "food and shopping"
            duration = 3
            start_date = "2025-08-10"

            response = process_travel_query(city, query, interests, duration, start_date)
            await cl.Message(content=f"✅ Here's your trip plan:\n\n{response}").send()
        else:
            await cl.Message(content="❌ Couldn’t understand. Try: **Plan me a 3-day trip to Mumbai for food and culture.**").send()

    except Exception as e:
        await cl.Message(content=f"❌ Error occurred: {str(e)}").send()
