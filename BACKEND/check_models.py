import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: API Key not found in .env file")
else:
    genai.configure(api_key=api_key)
    
    print("🔍 Checking available models for your API key...\n")
    
    try:
        # List all models
        for m in genai.list_models():
            # We only care about models that can 'generateContent' (Chat models)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ AVAILABLE: {m.name}")
                
    except Exception as e:
        print(f"❌ Error connecting to Google: {e}")