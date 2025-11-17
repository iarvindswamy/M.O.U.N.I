# backend/rag/live_scraper.py

import requests
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.html_cleaner import clean_html

def scrape_url_live(url):
    """
    Fetches a URL in real-time, cleans it, and returns the text.
    Used when the user provides a specific link to analyze.
    """
    print(f"Live scraping URL: {url}")
    
    try:
        # Fake a browser user-agent so we don't get blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to retrieve URL. Status: {response.status_code}")
            return None
            
        # Convert messy HTML to clean text
        text = clean_html(response.text)
        
        if len(text) < 50:
            return None # Page was mostly empty
            
        return text

    except Exception as e:
        print(f"Error scraping live URL: {e}")
        return None