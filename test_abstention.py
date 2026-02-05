import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.state import AgentState
from src.graph.nodes.router import route_question
from src.graph.nodes.retriever import retrieve
from src.graph.nodes.generator import generate

def test_full_pipeline(question, expected_behavior="answer"):
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
    
    # 1. Router
    print("\n[1] Running Router...")
    next_node = route_question(state)
    print(f"Router Intent: {state['intent']}")

    if next_node == "general_chat":
        print(f"Routed to General Chat. (Expected behavior: {expected_behavior})")
        return

    # 2. Retriever
    print("\n[2] Running Retriever...")
    retrieved_update = retrieve(state)
    state.update(retrieved_update)
    print(f"Retrieved {len(state['documents'])} docs.")
    
    # 3. Generator
    print("\n[3] Running Generator...")
    gen_update = generate(state)
    state.update(gen_update)
    answer = state["generation"]
    
    print(f"\nFINAL ANSWER:\n{answer}")
    
    if expected_behavior == "abstain":
        if "I don't have verified information" in answer:
            print("✅ PASS: Correctly abstained.")
        else:
            print("❌ FAIL: Did not stain as expected.")
            
    elif expected_behavior == "policy":
        if "Policy" in str(state['documents']): # Rough check if policy doc was retrieved
             print("✅ PASS: Policy document retrieved.")
        else:
             print("⚠️ WARN: Policy document might not have been retrieved.")

if __name__ == "__main__":
    # Test 1: Irrelevant / Abstention (using a topic definitely not in vector store)
    # "How do I bake a cake?" might be routed to general chat or vector store if classification fails.
    # Let's try something technical but unrelated to the program, e.g., "How do I fix my car?"
    # Ideally router sends "How do I fix my car?" to general or vector store (intent might be 'general' or 'logistics' error).
    # If routed to vector_store, it should find no docs and abstain.
    test_full_pipeline("What is the recipe for lasagna?", expected_behavior="abstain")
    
    # Test 2: Standard Question
    test_full_pipeline("Is the ISA legally binding?", expected_behavior="answer")
    
    # Test 3: Policy Check
    test_full_pipeline("Is the deposit refundable?", expected_behavior="policy")
