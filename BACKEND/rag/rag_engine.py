# backend/rag/rag_engine.py

import faiss
import pickle
import os
import numpy as np
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.gemini_client import embed_query, ask_gemini

# --- Constants ---
# We use absolute paths relative to this file to avoid "file not found" errors
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_FILE = os.path.join(BASE_DIR, "rag/vector_store.faiss")
INDEX_FILE = os.path.join(BASE_DIR, "rag/index.pkl")

# --- Load Database (Global Variables) ---
# We load these ONCE when the server starts to make chat fast.
print("Loading RAG Database...")
index = None
documents = []

if os.path.exists(VECTOR_DB_FILE) and os.path.exists(INDEX_FILE):
    try:
        index = faiss.read_index(VECTOR_DB_FILE)
        with open(INDEX_FILE, "rb") as f:
            documents = pickle.load(f)
        print(f"Database loaded successfully. {len(documents)} documents indexed.")
    except Exception as e:
        print(f"Error loading database: {e}")
else:
    print("WARNING: No database found. Run 'process_data.py' first.")

def retrieve_context(query, k=5):
    """
    Searches the FAISS database for the 5 most relevant text chunks.
    """
    if index is None or not documents:
        return ""

    # 1. Convert user question to vector
    query_emb = embed_query(query)
    if not query_emb:
        return ""

    # 2. Search FAISS
    # We need a list of vectors, so we wrap it in a list
    search_vector = np.array([query_emb]).astype("float32")
    
    # distances, indices = index.search(vector, k)
    distances, indices = index.search(search_vector, k)

    # 3. Fetch the actual text
    retrieved_chunks = []
    for i in indices[0]:
        if i < len(documents) and i >= 0:
            retrieved_chunks.append(documents[i])

    return "\n\n".join(retrieved_chunks)

def rag_chat(query):
    """
    The main function for 'University Mode'.
    1. Retrieves data.
    2. Sends to Gemini with M.O.U.N.I persona instructions.
    """
    # 1. Get relevant info from our DB
    context = retrieve_context(query)
    
    # Default context if nothing found or database is empty
    if not context:
        context = "No specific university document found for this query."

    # 2. Create the M.O.U.N.I. Persona Prompt
    # This instructs the AI on its identity and how to behave.
    prompt = f"""
    SYSTEM INSTRUCTIONS:
    You are M.O.U.N.I. (Multifunctional Operational Unified Network Interface), the official AI assistant for Vignan University.
    
    GUIDELINES:
    1. If the user greets you (e.g., "hi", "hello", "hey"), START your response by strictly introducing yourself: 
       "Hello! I am M.O.U.N.I (Multifunctional Operational Unified Network Interface), your Vignan University Assistant. How can I help you today?"
    2. For all other questions, answer STRICTLY based on the "CONTEXT DATA" provided below.
    3. If the answer is not in the context, politely say you don't have that information in the university documents.
    4. Do NOT make up facts.
    5. Be professional, helpful, and concise.

    CONTEXT DATA:
    {context}
    
    USER QUESTION:
    {query}
    """

    # 3. Get answer from Gemini
    return ask_gemini(prompt)