# memory/faiss_memory.py

import os
import pickle
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

INDEX_PATH = "faiss_index/index.faiss"
PKL_PATH = "faiss_index/index.pkl"
DUMMY_DOC = "This is a dummy document for initializing FAISS."

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_or_create_vectorstore():
    if os.path.exists(INDEX_PATH) and os.path.exists(PKL_PATH):
        with open(PKL_PATH, "rb") as f:
            return FAISS.load_local(INDEX_PATH, embedding, index_name="faiss", docstore=pickle.load(f))
    else:
        print("⚠️ Creating new FAISS index...")
        vectorstore = FAISS.from_texts([DUMMY_DOC], embedding)
        save_vectorstore(vectorstore)
        return vectorstore

def save_vectorstore(vectorstore):
    os.makedirs("faiss_index", exist_ok=True)
    faiss_index = vectorstore.index
    with open(PKL_PATH, "wb") as f:
        pickle.dump(vectorstore.docstore, f)
    vectorstore.save_local(INDEX_PATH)

def store_response(query, response, vectorstore):
    vectorstore.add_texts([query + "\n\n" + response])
    save_vectorstore(vectorstore)

def check_for_similar_response(query, vectorstore, threshold=0.9):
    results = vectorstore.similarity_search(query, k=1)
    if results:
        score = results[0].metadata.get("score", 1.0)
        if score >= threshold:
            return results[0].page_content
    return None
