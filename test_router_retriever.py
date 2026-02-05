import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.state import AgentState
from src.graph.nodes.router import route_question
from src.graph.nodes.retriever import retrieve

def test_routing_and_retrieval(question, expected_intent=None):
    print(f"\n\n==================================================")
    print(f"TESTING QUERY: '{question}'")
    print(f"==================================================")
    
    # Mock State
    state = {
        "question": question,
        "documents": [],
        "intent": "",
        "target_collections": []
    }
    
    # 1. Test Router
    print("\n[1] Running Router...")
    next_node = route_question(state)
    print(f"Router Result -> Next Node: {next_node}")
    print(f"State Update -> Intent: {state['intent']} | Targets: {state['target_collections']}")
    
    if expected_intent and state['intent'] != expected_intent:
        print(f"❌ FAIL: Expected intent '{expected_intent}', got '{state['intent']}'")
    else:
        print(f"✅ PASS: Intent check")

    if next_node != "vector_store":
        print("Skipping retrieval (routed to general chat)")
        return

    # 2. Test Retriever
    print("\n[2] Running Retriever (with Reranking)...")
    try:
        new_state = retrieve(state)
        docs = new_state["documents"]
        print(f"Retrieved {len(docs)} top documents:")
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "unknown")
            snippet = doc.page_content.replace("\n", " ")[:100]
            print(f"  {i+1}. [{source}] {snippet}...")
            
    except Exception as e:
        print(f"❌ Retriever Error: {e}")

if __name__ == "__main__":
    # Test cases covering different intents
    test_routing_and_retrieval("What is the starting salary for graduates?", "placement")
    test_routing_and_retrieval("Is the ISA legally binding?", "financing")
    test_routing_and_retrieval("Do you teach Python and Deep Learning?", "curriculum")
    test_routing_and_retrieval("Is it a scam? I saw bad reviews.", "credibility")
    test_routing_and_retrieval("Hello", "general")
