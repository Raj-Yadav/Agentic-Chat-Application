"""
Ingestion Script.
Orchestrates the entire knowledge extraction pipeline:
1. Loads CSV/Markdown seed content.
2. Scrapes authoritative websites.
3. Processes and cleans data.
4. Chunks data into optimized segments.
5. Ingests data into 4 separate ChromaDB collections.
"""

import sys
import os

# Ensure src is in pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import AUTHORITATIVE_URLS
from src.ingestion.scraper import scrape_site
from src.ingestion.vector_db import create_vector_db
from src.ingestion.processor import process_decision_faq, process_policy_documents, process_web_content

def main() -> None:
    """
    Main execution function for knowledge ingestion.
    """
    print("Starting Phase 1: Knowledge Extraction & Architecture Rebuild...")
    
    # --- Layer 1: Decision FAQ ---
    print("\n[Layer 1] Processing Decision FAQ...")
    faq_chunks = process_decision_faq()
    if faq_chunks:
        create_vector_db(faq_chunks, collection_name="decision_faq")
    
    # --- Layer 2: Policy Documents ---
    print("\n[Layer 2] Processing Policy Documents...")
    policy_chunks = process_policy_documents()
    if policy_chunks:
        create_vector_db(policy_chunks, collection_name="policy")

    # --- Web Content (Layers 3 & 4) ---
    print("\n[Web Scrape] Scraping authoritative sources...")
    web_docs = scrape_site(AUTHORITATIVE_URLS, max_depth=2)
    
    if web_docs:
        print("\n[Layer 3 & 4] Processing Web Content...")
        program_chunks, trust_chunks = process_web_content(web_docs)
        
        if program_chunks:
            print(f"Storing {len(program_chunks)} Program Knowledge chunks...")
            create_vector_db(program_chunks, collection_name="program")
            
        if trust_chunks:
            print(f"Storing {len(trust_chunks)} Trust & Transparency chunks...")
            create_vector_db(trust_chunks, collection_name="trust")
    else:
        print("No web documents found.")

    print("\nPhase 1 Complete! Knowledge base separated into 4 layers.")

if __name__ == "__main__":
    main()
