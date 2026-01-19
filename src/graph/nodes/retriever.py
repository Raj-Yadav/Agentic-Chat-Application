from src.graph.state import AgentState
from src.ingestion.vector_db import create_vector_db
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.config import CHROMA_DB_DIR, OPENAI_API_KEY

def retrieve(state: AgentState):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Initialize Vector Store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )
    
    # Retrieval
    documents = vector_store.similarity_search(question, k=3)
    return {"documents": documents, "question": question}
