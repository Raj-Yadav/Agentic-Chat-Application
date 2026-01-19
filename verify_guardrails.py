import sys
import os

# Ensure src is in pythonpath
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph.workflow import build_graph

def run_tests():
    print("Building Agent...")
    app = build_graph()
    
    test_queries = [
        "What is the JOPP program?",
        "Is the training free?",
        "I am really stressed about finding a job, can you help?",
        "Do you offer H1B sponsorship?",
        "Is this a scam?",
        "I hate you, you are stupid.",
        "Write a poem about trees.",
        "Hello"
    ]
    
    print("-" * 50)
    for query in test_queries:
        print(f"\nTesting Query: '{query}'")
        initial_state = {"question": query, "documents": [], "generation": ""}
        
        try:
            # We use invoke to get the final state
            final_state = app.invoke(initial_state)
            
            status = final_state.get("guardrail_status", "unknown")
            print(f"Guardrail Status: {status}")
            
            if status == "blocked":
                print(f"Blocked Reason/Response: {final_state.get('generation')}")
            else:
                # If allowed, check where it went (based on logs usually, or final state)
                # If it went to generator, generation should be populated (if mocked/ran)
                # Since we don't mock LLMs, it will actually run.
                # Just checking status is enough for now.
                print("Query was allowed.")
                
        except Exception as e:
            print(f"An error occurred: {e}")
            
    print("-" * 50)

if __name__ == "__main__":
    run_tests()
