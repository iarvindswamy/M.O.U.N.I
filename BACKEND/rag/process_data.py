# backend/rag/process_data.py

import os
import pickle
import numpy as np
import faiss
import sys

# Add backend to path to import other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.gemini_client import embed_text
from crawler.pdf_reader import extract_pdf_text

# --- Settings ---
DATA_DIR = "data"
VECTOR_DB_FILE = "rag/vector_store.faiss"
INDEX_FILE = "rag/index.pkl"
CHUNK_SIZE = 1000  # How many characters per chunk
OVERLAP = 100      # Overlap ensures we don't cut sentences in half awkwardly

def load_raw_data():
    """
    Reads all files from data/pdfs and data/html
    Returns a list of dicts: [{'text': '...', 'source': 'filename'}]
    """
    raw_docs = []
    
    # 1. Read PDFs
    pdf_dir = os.path.join(DATA_DIR, "pdfs")
    if os.path.exists(pdf_dir):
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                path = os.path.join(pdf_dir, filename)
                print(f"Processing PDF: {filename}")
                text = extract_pdf_text(path)
                if text:
                    raw_docs.append({"text": text, "source": filename})

    # 2. Read HTML text files
    html_dir = os.path.join(DATA_DIR, "html")
    if os.path.exists(html_dir):
        for filename in os.listdir(html_dir):
            if filename.endswith(".txt"):
                path = os.path.join(html_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    raw_docs.append({"text": text, "source": filename})
    
    return raw_docs

def chunk_text(text, source):
    """
    Splits long text into smaller chunks for the AI.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append({"text": chunk, "source": source})
        start += CHUNK_SIZE - OVERLAP # Move forward, but overlap a bit
    return chunks

def build_vector_store():
    print("Step 1: Loading data from crawler folders...")
    raw_docs = load_raw_data()
    
    if not raw_docs:
        print("No data found! Did you run the crawler first?")
        return

    print(f"Step 2: Splitting {len(raw_docs)} documents into chunks...")
    chunked_docs = []
    for doc in raw_docs:
        new_chunks = chunk_text(doc["text"], doc["source"])
        chunked_docs.extend(new_chunks)
    
    print(f"Total chunks created: {len(chunked_docs)}")

    print("Step 3: Generating Embeddings (This calls Gemini API)...")
    embeddings = []
    final_docs = [] # We only keep docs that successfully got an embedding

    # Process in batches to be safe
    for i, doc in enumerate(chunked_docs):
        emb = embed_text(doc["text"])
        if emb:
            embeddings.append(emb)
            final_docs.append(doc["text"]) # Store just text for retrieval
            # Optional: print progress every 10 chunks
            if i % 10 == 0:
                print(f"Embedded {i}/{len(chunked_docs)} chunks...")
        else:
            print(f"Skipped chunk {i} due to error.")

    if not embeddings:
        print("Failed to generate embeddings.")
        return

    print("Step 4: Saving to FAISS database...")
    # Convert to numpy array for FAISS
    embedding_matrix = np.array(embeddings).astype("float32")
    
    # Create FAISS index
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(embedding_matrix)

    # Save to disk
    faiss.write_index(index, VECTOR_DB_FILE)
    with open(INDEX_FILE, "wb") as f:
        pickle.dump(final_docs, f)

    print("SUCCESS: Database built!")
    print(f"Saved {VECTOR_DB_FILE} and {INDEX_FILE}")

if __name__ == "__main__":
    build_vector_store()