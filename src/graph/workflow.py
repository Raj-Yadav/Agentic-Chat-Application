"""
Workflow Module.
Defines the LangGraph state machine, nodes, and conditional edges that orchestrate the chat application.
"""

from typing import Literal, Any, Dict
from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes.router import route_question
from src.graph.nodes.retriever import retrieve
from src.graph.nodes.grader import grade_documents
from src.graph.nodes.generator import generate
from src.graph.nodes.query_rewriter import rewrite_query
from src.graph.nodes.input_guardrails import input_guardrails
from src.utils.cache import cache

def check_cache(state: AgentState) -> Dict[str, Any]:
    """
    Check Redis cache for existing answer.
    """
    print("---CHECK CACHE---")
    question = state["question"]
    cached_response = cache.get(question)
    
    if cached_response:
        print("---CACHE HIT---")
        return {"generation": cached_response, "cache_hit": True}
    
    print("---CACHE MISS---")
    return {"cache_hit": False}

def route_cache(state: AgentState) -> Literal["end", "router"]:
    """
    Route based on cache hit.
    """
    if state.get("cache_hit"):
        return "end"
    return "router"

def route_guardrails(state: AgentState) -> Literal["router", "end"]:
    """
    Route based on guardrail status.

    Args:
        state (AgentState): The current graph state.
    
    Returns:
        Literal["router", "end"]: Next node to transition to.
    """
    if state.get("guardrail_status") == "blocked":
        return "end"
    return "router"

def route_from_router(state: AgentState) -> Literal["generator", "retriever"]:
    """
    Route based on router decision.

    Args:
        state (AgentState): The current graph state.
    
    Returns:
        Literal["generator", "retriever"]: Next node to transition to.
    """
    if state.get("datasource") == "general_chat":
        return "generator" # Bypass retriever
    return "retriever"

def decide_to_generate(state: AgentState) -> Literal["generate", "rewrite_query"]:
    """
    Determines whether to generate an answer or re-generate a question based on document relevance.

    Args:
        state (AgentState): The current graph state.

    Returns:
        Literal["generate", "rewrite_query"]: Next node decision.
    """
    filtered_documents = state.get("documents", [])

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        if state.get("loop_step", 0) >= 2:
            print("---DECISION: MAX RETRIES REACHED, GENERATING---")
            return "generate"
        
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
        return "rewrite_query"
    else:
        # We have relevant documents, so generate answer
        return "generate"

def build_graph() -> Any:
    """
    Constructs the LangGraph workflow.

    Returns:
        Any: The compiled workflow application.
    """
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("input_guardrails", input_guardrails)
    workflow.add_node("router", route_question)
    workflow.add_node("retriever", retrieve)
    workflow.add_node("grader", grade_documents)
    workflow.add_node("query_rewriter", rewrite_query)
    workflow.add_node("generator", generate)

    # Build graph
    workflow.set_entry_point("input_guardrails")
    
    workflow.add_conditional_edges(
        "input_guardrails",
        route_guardrails,
        {
            "router": "check_cache",
            "end": END
        }
    )

    workflow.add_node("check_cache", check_cache)
    
    workflow.add_conditional_edges(
        "check_cache",
        route_cache,
        {
            "end": END,
            "router": "router"
        }
    )
    
    workflow.add_conditional_edges(
        "router",
        route_from_router,
        {
            "retriever": "retriever",
            "generator": "generator"
        }
    )

    workflow.add_edge("retriever", "grader")
    
    workflow.add_conditional_edges(
        "grader",
        decide_to_generate,
        {
            "rewrite_query": "query_rewriter",
            "generate": "generator",
        },
    )
    
    # Send back to router to re-evaluate intent after query rewrite
    # This ensures that if the query changes significantly, we target the right collections again.
    workflow.add_edge("query_rewriter", "router") 
    
    workflow.add_edge("generator", END)

    # Compile
    app = workflow.compile()
    return app
