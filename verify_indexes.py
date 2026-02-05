import sys
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import CHROMA_DB_DIR, OPENAI_API_KEY

def verify_collection(name):
    print(f"\n--- Verifying Collection: {name} ---")
    try:
        if not OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY not found.")
            return

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = Chroma(
            collection_name=name,
            embedding_function=embeddings,
            persist_directory=CHROMA_DB_DIR
        )
        
        # Get count (using underlying collection)
        # Chroma in Langchain wraps the client. 
        # We can try to get some documents via similarity search to ensure it works.
        results = vector_store.similarity_search("tuition", k=1)
        
        print(f"Collection '{name}' accessible.")
        if results:
            print(f"Found {len(results)} document used query 'tuition'.")
            print(f"Sample Metadata: {results[0].metadata}")
        else:
            print("No documents found (migth be empty or query mismatch).")
            
    except Exception as e:
        print(f"Error accessing collection {name}: {e}")

if __name__ == "__main__":
    verify_collection("decision_faq")
    verify_collection("policy")
    # program and trust might be empty if we interrupted scraping
    verify_collection("program") 
