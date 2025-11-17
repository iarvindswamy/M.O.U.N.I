# backend/llm/gemini_client.py

import google.generativeai as genai
import sys
import os

# --- Path Setup ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- 🏆 MODEL CONFIGURATION (UPDATED) ---
# We are using your available "gemini-2.5-flash" for the best speed/accuracy balance.
MODEL_NAME = "gemini-2.5-flash"

# Standard embedding model (usually works with all accounts)
EMBEDDING_MODEL = "models/text-embedding-004"

def ask_gemini(prompt):
    """
    Sends a prompt to Gemini and gets the text response.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        
        # --- FALLBACK LOGIC ---
        # If 2.5 Flash fails, try the "Latest Pro" alias which is very safe
        if "404" in str(e) or "not found" in str(e):
            print("⚠️ Primary model failed. Switching to 'gemini-pro-latest'...")
            try:
                fallback_model = genai.GenerativeModel("gemini-pro-latest")
                response = fallback_model.generate_content(prompt)
                return response.text
            except Exception as e2:
                return f"Server Error: {e2}"
                
        return "I'm having trouble connecting to the AI server right now."

def embed_text(text):
    """
    Converts document text into a vector list for storage.
    """
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result["embedding"]
    except Exception as e:
        print(f"❌ Embedding Error: {e}")
        return []

def embed_query(text):
    """
    Converts a USER QUESTION into a vector for searching.
    """
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]
    except Exception as e:
        print(f"❌ Query Embedding Error: {e}")
        return []