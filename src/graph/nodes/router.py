"""
Router Module.
Classifies user intent and routes questions to the appropriate data source (vector store or general chat).
"""

from typing import Literal, Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from src.graph.state import AgentState
from src.config import OPENAI_API_KEY
from langsmith import traceable

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource and classify intent."""
    intent: Literal["financing", "placement", "curriculum", "logistics", "credibility", "general"] = Field(
        ...,
        description="Classify the user query into one of the following categories: financing, placement, curriculum, logistics, credibility, or general."
    )
    datasource: Literal["vector_store", "general_chat"] = Field(
        ...,
        description="Choose 'vector_store' for specific questions about the program/company, or 'general_chat' for greeting/off-topic.",
    )

@traceable
def route_question(state: AgentState) -> Dict[str, Any]:
    """
    Route question to web search or vectorstore.

    Args:
        state (AgentState): The current graph state.
    
    Returns:
        Dict[str, Any]: Updated state with 'intent', 'target_collections', and 'datasource'.
    """
    print("---ROUTE QUESTION---")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    structured_llm_router = llm.with_structured_output(RouteQuery)
    
    system = """Classify SynergisticIT user intent & datasource.

    1. Analyze input.
    2. Select Category & Datasource.

    **Categories**:
    - **financing**: ISA, tuition, loans, repayment, deposit, refunds.
    - **placement**: Job guarantee, success rate, hiring partners, visa (H1B/OPT), salary.
    - **curriculum**: Technologies (Java, Python, AWS, AI), projects, skills, syllabus.
    - **logistics**: Schedule, duration, start dates, remote/onsite.
    - **credibility**: Legitimacy, reviews, scams, alumni, locations.
    - **general**: Greetings, off-topic.

    **Sources**:
    - `vector_store`: financing, placement, curriculum, logistics, credibility.
    - `general_chat`: general ONLY.
    """
    
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    
    question_router = route_prompt | structured_llm_router
    
    question = state["question"]
    source = question_router.invoke({"question": question})
    
    # Map intent to target collections
    intent = source.intent
    target_collections: List[str] = []
    
    if intent == "financing":
        target_collections = ["decision_faq", "policy"]
        source.datasource = "vector_store" # Enforce consistency
    elif intent == "placement":
        target_collections = ["decision_faq", "policy", "trust"]
        source.datasource = "vector_store"
    elif intent == "curriculum":
        target_collections = ["program"]
        source.datasource = "vector_store"
    elif intent == "logistics":
        target_collections = ["decision_faq", "program", "trust"]
        source.datasource = "vector_store"
    elif intent == "credibility":
        target_collections = ["trust", "decision_faq"]
        source.datasource = "vector_store"
    elif intent == "general":
        if source.datasource == "vector_store":
             target_collections = ["decision_faq", "program"] # fallback
        else:
             target_collections = []

    print(f"---ROUTED TO: {source.datasource} (Intent: {intent})---")
    
    # Update state
    return {
        "intent": intent, 
        "target_collections": target_collections,
        "datasource": source.datasource
    }
