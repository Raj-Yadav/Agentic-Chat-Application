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
    
    system = """You are an expert at routing user questions about SynergisticIT.
    Classify the intent into one of 6 categories:
    1. financing: ISA, tuition, loans, repayment, salary threshold, deposit.
    2. placement: Job guarantee, success rate, companies, visa support (H1B/OPT), average salary.
    3. curriculum: Technologies (Java, Python, AWS), projects, coding, skills.
    4. logistics: Schedule, duration, remote vs onsite, start dates.
    5. credibility: Reviews, scam allegations, real office, alumni, legitimacy.
    6. general: Greetings, "how are you", or off-topic questions not about the program.

    Also choose the datasource:
    - vector_store: for financing, placement, curriculum, logistics, credibility.
    - general_chat: only for 'general' intent if it's just a greeting or unrelated topic.
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
    elif intent == "placement":
        target_collections = ["decision_faq", "policy", "trust"]
    elif intent == "curriculum":
        target_collections = ["program"]
    elif intent == "logistics":
        target_collections = ["decision_faq", "program", "trust"]
    elif intent == "credibility":
        target_collections = ["trust", "decision_faq"]
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
