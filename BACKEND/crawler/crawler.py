# backend/crawler/crawler.py

import os
import time
import re
import requests
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sys

# Add the backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BASE_URL
from html_cleaner import clean_html

# --- Settings ---
MAX_DEPTH = 2
MAX_PAGES = 50  # Safety limit to prevent crawling forever
DATA_PDF_DIR = "data/pdfs"
DATA_HTML_DIR = "data/html"

os.makedirs(DATA_PDF_DIR, exist_ok=True)
os.makedirs(DATA_HTML_DIR, exist_ok=True)

visited_urls = set()
pages_crawled = 0

def sanitize_filename(url):
    """Converts a URL into a safe filename."""
    parsed = urlparse(url)
    clean_name = re.sub(r"[^a-zA-Z0-9]", "_", parsed.path)
    if not clean_name or clean_name == "_":
        clean_name = "index"
    return clean_name[:50]

def download_pdf_direct(url):
    """Downloads a PDF using standard requests (lighter than browser)."""
    try:
        response = requests.get(url, timeout=10, stream=True)
        if response.status_code == 200:
            filename = sanitize_filename(url) + ".pdf"
            path = os.path.join(DATA_PDF_DIR, filename)
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"[PDF] Saved: {filename}")
    except Exception as e:
        print(f"[Error] PDF Download failed {url}: {e}")

def run_crawler():
    global pages_crawled
    
    # Start the Playwright Browser
    with sync_playwright() as p:
        print("Launching Headless Browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # We use a queue for URLs to visit (Breadth-First Search)
        # Tuple: (url, current_depth)
        queue = [(BASE_URL, 0)]
        
        while queue and pages_crawled < MAX_PAGES:
            url, depth = queue.pop(0)
            
            if url in visited_urls:
                continue
            if depth > MAX_DEPTH:
                continue
            
            visited_urls.add(url)
            pages_crawled += 1
            
            print(f"[{pages_crawled}/{MAX_PAGES}] Crawling (Depth {depth}): {url}")
            
            try:
                # 1. Visit the page
                # 'networkidle' waits until network activity stops (JS finished)
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
                
                # Wait a tiny bit more for React to render specific divs
                page.wait_for_timeout(1000) 
                
                # 2. Get the rendered HTML
                content = page.content()
                
                # 3. Save HTML Text
                text = clean_html(content)
                if len(text) > 100: # Only save if meaningful content found
                    filename = sanitize_filename(url) + ".txt"
                    with open(os.path.join(DATA_HTML_DIR, filename), "w", encoding="utf-8") as f:
                        f.write(f"Source: {url}\n\n{text}")
                    print(f"   -> Saved HTML Content")

                # 4. Extract Links for next round
                # We parse content with BeautifulSoup because it's easier than Playwright selectors
                soup = BeautifulSoup(content, "html.parser")
                
                for a_tag in soup.find_all("a", href=True):
                    link = a_tag["href"]
                    full_url = urljoin(url, link)
                    
                    # Remove hash anchors (#section)
                    full_url = full_url.split("#")[0]
                    
                    if full_url in visited_urls:
                        continue
                        
                    # Handle PDFs
                    if full_url.lower().endswith(".pdf"):
                        if full_url not in visited_urls:
                            download_pdf_direct(full_url)
                            visited_urls.add(full_url)
                            
                    # Handle Internal Links
                    elif "vignan.ac.in" in full_url:
                        # Avoid logout links or irrelevant pages
                        if "logout" not in full_url and "javascript" not in full_url:
                            queue.append((full_url, depth + 1))
                            
            except Exception as e:
                print(f"   [Error] Failed to process {url}: {e}")

        browser.close()
        print("Crawling Finished.")

if __name__ == "__main__":
    run_crawler()