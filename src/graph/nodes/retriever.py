"""
Retriever Module.
Handles document retrieval from targeted ChromaDB collections and re-ranking of results.
"""

from typing import Dict, Any, List, Optional
from src.graph.state import AgentState
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from src.config import CHROMA_DB_DIR, OPENAI_API_KEY
from sentence_transformers import CrossEncoder
from langsmith import traceable

# Global reranker initialization (lazy load)
_RERANKER: Optional[CrossEncoder] = None

def get_reranker() -> CrossEncoder:
    """
    Lazy loads the CrossEncoder model to avoid overhead if not used.
    """
    global _RERANKER
    if _RERANKER is None:
        print("Loading CrossEncoder model...")
        _RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return _RERANKER

@traceable
def retrieve(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve documents from targeted collections and rerank them using CrossEncoder.

    Args:
        state (AgentState): The current graph state.
    
    Returns:
        Dict[str, Any]: Updated state with 'documents'.
    """
    print("---RETRIEVE & RERANK---")
    question = state["question"]
    target_collections = state.get("target_collections", [])
    
    # Default to all if empty or error
    if not target_collections:
        print("WARNING: No target collections found. Defaulting to 'program'.")
        target_collections = ["program"]

    print(f"Target Collections: {target_collections}")
    
    # 1. Retrieve (High Recall)
    pre_rerank_docs = []
    for collection_name in target_collections:
        try:
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY),
                persist_directory=CHROMA_DB_DIR,
            )
            # Fetch more docs initially for reranking
            results = vectorstore.similarity_search(question, k=25)
            # Add metadata to track source
            for doc in results:
                doc.metadata["_source_collection"] = collection_name
                pre_rerank_docs.append(doc)
            print(f"  - Retrieved {len(results)} from '{collection_name}'")
        except Exception as e:
            print(f"  - Error retrieving from '{collection_name}': {e}")
            
    if not pre_rerank_docs:
        return {"documents": [], "question": question}
    
    # Deduplicate (if any)
    # Deduplicate (if any)
    unique_docs = {doc.page_content: doc for doc in pre_rerank_docs}.values()
    pre_rerank_docs = list(unique_docs)

    # 2. Rerank
    # CrossEncoder needs pairs of (query, doc_text)
    pairs = [(question, doc.page_content) for doc in pre_rerank_docs]
    
    # Lazy load model if not already (to avoid startup lag)
    reranker_model = get_reranker()
        
    scores = reranker_model.predict(pairs)
    
    # Attach scores and sort
    scored_docs = sorted(
        zip(pre_rerank_docs, scores), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Select Top K (e.g., 3)
    # Select Top K (e.g., 3)
    top_k_docs = [doc for doc, score in scored_docs[:3]]

    return {"documents": top_k_docs, "question": question}
