"""
Vector Database module.
Handles creation, update, and persistence of ChromaDB collections.
"""

from typing import List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import CHROMA_DB_DIR, OPENAI_API_KEY

def create_vector_db(chunks: List[Document], collection_name: str = "default_collection") -> Chroma:
    """
    Creates or updates the vector database for a specific collection.

    Args:
        chunks (List[Document]): The document chunks to store.
        collection_name (str): The name of the collection (e.g., 'decision_faq', 'policy').

    Returns:
        Chroma: The initialized vector store object.

    Raises:
        ValueError: If OPENAI_API_KEY is missing.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in environment variables.")

    print(f"Initializing Vector DB at {CHROMA_DB_DIR} for collection: {collection_name}...")
    
    # Initialize OpenAI Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create Chroma VectorStore
    # Using from_documents will automatically add them to the persistent store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_DB_DIR
    )
    
    print(f"Vector database for {collection_name} created/updated successfully.")
    return vector_store
