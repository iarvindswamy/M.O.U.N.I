# backend/crawler/pdf_reader.py

import fitz  # This is PyMuPDF

def extract_pdf_text(filepath):
    """
    Opens a PDF file and returns all text as a single string.
    """
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
        return ""