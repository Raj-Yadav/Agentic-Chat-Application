import sys
import os

# Ensure src is in pythonpath if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.graph.workflow import build_graph

app = FastAPI(title="Agentic Chat API")

# Initialize the graph once
graph = build_graph()

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to interact with the Agentic Chat.
    Accepts a question and returns the agent's response.
    """
    initial_state = {"question": request.question, "documents": [], "generation": ""}
    
    try:
        # Use invoke to run the graph to completion
        result = graph.invoke(initial_state)
        
        # Extract the generation from the final state
        if "generation" in result:
            return ChatResponse(answer=result["generation"])
        elif "guardrail_status" in result and result["guardrail_status"] == "blocked":
             # Handle case where it might have been blocked and generation key might differ in some implementations, 
             # but our input_guardrails returns 'generation' on block too.
             # If it just returns status, we need to handle that.
             # Check input_guardrails.py: it returns 'generation' key on block.
             # If allowed, it goes to other nodes. 
             # If it finishes without 'generation' (unlikely for this graph), return fallback.
             return ChatResponse(answer="Request was blocked but no explanation provided.")
        else:
            return ChatResponse(answer="No response generated.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Run the app using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
