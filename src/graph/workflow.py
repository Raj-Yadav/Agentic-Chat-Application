from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes.router import route_question
from src.graph.nodes.retriever import retrieve
from src.graph.nodes.grader import grade_documents
from src.graph.nodes.generator import generate
from src.graph.nodes.generator import generate
from src.graph.nodes.query_rewriter import rewrite_query
from src.graph.nodes.input_guardrails import input_guardrails

def route_guardrails(state):
    """
    Route based on guardrail status. If allowed, then route based on question.
    """
    if state.get("guardrail_status") == "blocked":
        return "end"
    
    # If allowed, proceed to standard routing
    return route_question(state)

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """
    print("---ASSESS GRADED DOCUMENTS---")
    filtered_documents = state["documents"]

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
        print("---DECISION: GENERATE---")
        return "generate"

def build_graph():
    """
    Constructs the LangGraph workflow.
    """
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("input_guardrails", input_guardrails)
    workflow.add_node("router", route_question) # This is actually just a conditional edge usually, but let's see how we want to model it.
    # Actually, the router is best modeled as a conditional entry point or a first node.
    # Let's model it as a function that returns the next destination.
    
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
            "vector_store": "retriever",
            "general_chat": "generator",
            "end": END
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
    
    workflow.add_edge("query_rewriter", "retriever")
    workflow.add_edge("generator", END)

    # Compile
    app = workflow.compile()
    return app
