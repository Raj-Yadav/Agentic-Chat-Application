
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.vector_db import create_vector_db
from src.ingestion.processor import load_markdown_as_documents, chunk_text
from src.config import DATA_DIR

def ingest_manual():
    print("Starting Manual Ingestion for Program & Trust Layers...")
    
    # 1. Program Layer
    program_path = os.path.join(DATA_DIR, "seed_content", "program_manual.md")
    if os.path.exists(program_path):
        print(f"Processing Program Manual: {program_path}")
        docs = load_markdown_as_documents(program_path)
        # Add metadata
        for d in docs:
            d.metadata["category"] = "curriculum"
            d.metadata["intent"] = "informational"
            d.metadata["risk_level"] = "low"
            d.metadata["answer_type"] = "factual"
            d.metadata["source"] = "program_manual"
            
        chunks = chunk_text(docs, chunk_size=500, chunk_overlap=50)
        create_vector_db(chunks, collection_name="program")
        print(f"Ingested {len(chunks)} chunks into 'program'.")
    else:
        print(f"ERROR: {program_path} not found.")

    # 2. Trust Layer
    trust_path = os.path.join(DATA_DIR, "seed_content", "trust_manual.md")
    if os.path.exists(trust_path):
        print(f"Processing Trust Manual: {trust_path}")
        docs = load_markdown_as_documents(trust_path)
        # Add metadata
        for d in docs:
            d.metadata["category"] = "credibility"
            d.metadata["intent"] = "decision"
            d.metadata["risk_level"] = "medium"
            d.metadata["answer_type"] = "policy" # treat as authoritative
            d.metadata["source"] = "trust_manual"
            
        chunks = chunk_text(docs, chunk_size=500, chunk_overlap=50)
        create_vector_db(chunks, collection_name="trust")
        print(f"Ingested {len(chunks)} chunks into 'trust'.")
    else:
        print(f"ERROR: {trust_path} not found.")

if __name__ == "__main__":
    ingest_manual()
