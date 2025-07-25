# utils/input_parser.py

from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

class TravelInput(BaseModel):
    city: str = Field(..., description="City name for the trip")
    duration: int = Field(..., description="Number of days for the trip")
    interests: str = Field(..., description="Main interests like food, history, lakes")

def get_user_input_parser():
    parser = PydanticOutputParser(pydantic_object=TravelInput)

    prompt = PromptTemplate.from_template(
        template=(
            "Extract structured data from the following user request:\n"
            "Request: {input}\n\n"
            "Return JSON with city, duration (number only), and interests."
            "\n{format_instructions}"
        ),
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0,api_key= os.getenv("GEMINI_API_KEY"))
    chain = prompt | model | parser
    return chain
