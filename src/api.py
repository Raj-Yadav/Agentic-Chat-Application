"""
FastAPI Server.
Exposes the Agentic Chat application via a RESTful API endpoint.
"""

import sys
import os

# Ensure src is in pythonpath if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.graph.workflow import build_graph

app = FastAPI(title="Agentic Chat API", description="API for SynergisticIT Agentic Chatbot")

# Initialize the graph once
graph = build_graph()

class ChatRequest(BaseModel):
    """Request schema for the chat endpoint."""
    question: str = Field(..., description="The user's question.")

class ChatResponse(BaseModel):
    """Response schema for the chat endpoint."""
    answer: str = Field(..., description="The generated answer.")
    relevance_score: str = Field("N/A", description="Relevance score of retrieved documents.")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to interact with the Agentic Chat.
    Accepts a question and returns the agent's response.
    """
    initial_state = {"question": request.question, "documents": [], "generation": "", "relevance_score": "0/0"}
    
    try:
        # Use invoke to run the graph to completion
        result = graph.invoke(initial_state)
        
        # Extract the generation from the final state
        score = result.get("relevance_score", "N/A")
        
        if "generation" in result:
            return ChatResponse(answer=result["generation"], relevance_score=score)
        elif "guardrail_status" in result and result["guardrail_status"] == "blocked":
            # If blocked, the message might be in 'generation' or we handle it here
             return ChatResponse(answer="Request was blocked but no explanation provided.", relevance_score=score)
        else:
            return ChatResponse(answer="No response generated.", relevance_score=score)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Run the app using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
