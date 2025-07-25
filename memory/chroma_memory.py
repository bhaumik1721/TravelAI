# memory/chroma_memory.py

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

gemini_key = os.getenv("GEMINI_API_KEY")

load_dotenv()
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=gemini_key)

# Initialize Chroma vector store
chroma = Chroma(collection_name="travel_history", embedding_function=embedding, persist_directory="./chroma_db")

# Get retriever with compression (optional but good)
def get_retriever() -> VectorStoreRetriever:
    return chroma.as_retriever(search_kwargs={"k": 3})

# Add new document to memory
def add_to_chroma_memory(query: str, response: str):
    doc = Document(page_content=response, metadata={"query": query})
    chroma.add_documents([doc])

# Retrieve context for a new query
def retrieve_similar_context(query: str):
    retriever = get_retriever()
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])
