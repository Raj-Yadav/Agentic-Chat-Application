import sys
import os

# Ensure src is in pythonpath
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import AUTHORITATIVE_URLS
from src.ingestion.scraper import scrape_site
from src.ingestion.chunker import chunk_text
from src.ingestion.vector_db import create_vector_db

def main():
    print("Starting Phase 1: Knowledge Extraction...")
    
    # 1. Scrape
    print(f"Scraping authoritative sources...")
    # Scrape specific URLs
    docs = scrape_site(AUTHORITATIVE_URLS, max_depth=0) # max_depth=0 to strictly follow the list, or 1 for slight expansion
    
    if not docs:
        print("No documents found. Exiting.")
        return

    # 2. Chunk
    chunks = chunk_text(docs)
    
    # 3. Store in Vector DB
    create_vector_db(chunks)
    
    print("Phase 1 Complete!")

if __name__ == "__main__":
    main()
