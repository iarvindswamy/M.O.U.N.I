# backend/crawler/html_cleaner.py

from bs4 import BeautifulSoup
import re

def clean_html(html_content):
    """
    Takes raw HTML string, removes scripts/styles/tags,
    and returns clean, readable text.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Remove javascript and css
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.extract()

    # 2. Get text
    text = soup.get_text()

    # 3. Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # 4. Drop blank lines
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text