import os
import sys
import asyncio
from dotenv import load_dotenv

# Setup paths and env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from utils.google_places import get_places_by_city
from utils.input_parser import get_user_input_parser
from agents.langchain_faiss_agent import process_travel_query

import chainlit as cl

# Load environment variables
load_dotenv()


@cl.on_message
async def handle_message(message: cl.Message):
    user_input = message.content.strip()

    # Show typing status
    thinking = cl.Message(content="🤖 Thinking...")
    await thinking.send()

    try:
        # Use LangChain Output Parser to handle free-form input
        parser_chain = get_user_input_parser()
        parsed = parser_chain.invoke({"input": user_input})

        # Extract structured values
        city = parsed.city
        duration = parsed.duration
        interests = parsed.interests
        query = "tourist attractions"  # You can make this dynamic if needed

        # Get places for the parsed city
        places = get_places_by_city(city, keyword=query)

        # Final response (pass all required args)
        response = process_travel_query(city, query, interests, duration, places)

        # Update Chainlit UI with result
        thinking.content = f"✅ Here's your {duration}-day plan for {city} based on your interest in {interests}:\n\n{response}"
        await thinking.update()

    except Exception as e:
        # Show error in frontend
        thinking.content = f"❌ Error: {str(e)}"
        await thinking.update()
