import os
import sys
import asyncio

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith import Client
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langchain_openai import ChatOpenAI
from src.graph.workflow import build_graph
from src.config import OPENAI_API_KEY

# Initialize Client
client = Client()

# Initialize App
app = build_graph()

# Define dataset
dataset_name = "Agentic Chat App Evaluation"
dataset_description = "Evaluation dataset for SynergisticIT Agentic Chat Application"

# Example Questions & Expected Answers (Ground Truth)
examples = [
    {
        "inputs": {"question": "What is the refund policy?"},
        "outputs": {"expected": "The refund policy depends on the specific course and timeframe. Generally, full refunds are available within the first week, but please check the specific terms in the trust manual."} # Placeholder expected answer
    },
    {
        "inputs": {"question": "Do you offer job placement support?"},
        "outputs": {"expected": "Yes, SynergisticIT offers job placement support as part of its program."}
    },
    {
        "inputs": {"question": "How long is the Java track?"},
        "outputs": {"expected": "The Java track duration varies but typically spans several months including project work."}
    }
]

def create_dataset():
    """Check if dataset exists, if not create it."""
    try:
        if client.has_dataset(dataset_name=dataset_name):
            print(f"Dataset '{dataset_name}' already exists.")
            return client.read_dataset(dataset_name=dataset_name)
    except Exception:
        pass

    print(f"Creating dataset '{dataset_name}'...")
    dataset = client.create_dataset(
        dataset_name=dataset_name, 
        description=dataset_description
    )
    
    # Add examples
    client.create_examples(
        inputs=[e["inputs"] for e in examples],
        outputs=[e["outputs"] for e in examples],
        dataset_id=dataset.id
    )
    return dataset

# Define the target function (the agent)
def predict(inputs: dict) -> dict:
    """Run the agent on a single input."""
    question = inputs["question"]
    # Run the graph
    # app.invoke returns the final state. We want 'generation'.
    result = app.invoke({"question": question})
    return {"generation": result.get("generation", "No response")}

async def main():
    print("Initializing LangSmith Evaluation...")
    
    # 1. Create/Get Dataset
    create_dataset()
    
    # 2. Define Evaluators
    # Correctness evaluator (checks if answer matches ground truth using LLM)
    qa_evaluator = LangChainStringEvaluator(
        "cot_qa", 
        config={"llm": ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)}
    )
    
    # 3. Run Evaluation
    print("Running evaluation...")
    results = evaluate(
        predict,
        data=dataset_name,
        evaluators=[qa_evaluator],
        experiment_prefix="agent-eval-v1",
        max_concurrency=2
    )
    
    print("\nEvaluation Complete!")
    print(f"View results at: {results.experiment_results_url}")

if __name__ == "__main__":
    asyncio.run(main())
