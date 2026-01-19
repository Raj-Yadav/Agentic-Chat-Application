import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import CHROMA_DB_DIR, OPENAI_API_KEY

def create_vector_db(chunks):
    """
    Creates or updates the vector database with the given chunks.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in environment variables.")

    print(f"Initializing Vector DB at {CHROMA_DB_DIR}...")
    
    # Initialize OpenAI Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create Chroma VectorStore
    # Using from_documents will automatically add them to the persistent store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    
    print("Vector database created/updated successfully.")
    return vector_store
