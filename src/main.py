import sys
import os

# Ensure src is in pythonpath
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph.workflow import build_graph

def main():
    print("Initializing Agent...")
    app = build_graph()
    print("Agent Ready! Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            initial_state = {"question": user_input, "documents": [], "generation": ""}
            
            # Stream the graph
            for output in app.stream(initial_state):
                for key, value in output.items():
                    # We can optionally print steps here e.g. "Thinking..."
                    # print(f"Node '{key}' executed.")
                    if "generation" in value:
                        print(f"\nAgent: {value['generation']}")
                        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
