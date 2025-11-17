# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# 1. Get the Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Define the Base URL for the crawler
BASE_URL = "https://www.vignan.ac.in"

# Validation check
if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY is missing in .env file!")