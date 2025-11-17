# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# --- Import our custom modules ---
# We need these to talk to the AI and the database
from llm.gemini_client import ask_gemini
from rag.rag_engine import rag_chat
from rag.live_scraper import scrape_url_live

app = FastAPI()

# --- CORS Configuration ---
# This allows your React Frontend (running on localhost:5173)
# to talk to this Python Backend (running on localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Model ---
# This defines what data the frontend must send us
class ChatRequest(BaseModel):
    message: str
    mode: str          # "general" or "university"
    link: str = None   # Optional: If the user provides a specific URL

@app.get("/")
def read_root():
    return {"status": "running", "message": "Vignan Chatbot Backend is Online"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    The main chat handler.
    Decides which logic to use based on user input.
    """
    try:
        user_msg = request.message
        mode = request.mode
        link = request.link

        # --- CASE 1: User provided a specific Link ---
        if link:
            print(f"[Mode: LIVE LINK] Processing {link}")
            # Scrape the link in real-time
            page_text = scrape_url_live(link)
            
            if not page_text:
                return {"response": "I couldn't read that link. It might be blocked or empty."}
            
            # Ask Gemini to answer using ONLY that page's text
            prompt = f"""
            Read this website content and answer the user's question.
            
            WEBSITE CONTENT:
            {page_text[:10000]}  # Limit text to avoid token limits

            USER QUESTION:
            {user_msg}
            """
            response = ask_gemini(prompt)
            return {"response": response}

        # --- CASE 2: University Mode (RAG) ---
        if mode == "university":
            print(f"[Mode: UNIVERSITY] Searching database...")
            response = rag_chat(user_msg)
            return {"response": response}

        # --- CASE 3: General Mode ---
        else:
            print(f"[Mode: GENERAL] Asking Gemini directly...")
            response = ask_gemini(user_msg)
            return {"response": response}

    except Exception as e:
        print(f"SERVER ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# To run this server, type in terminal:
# uvicorn main:app --reload