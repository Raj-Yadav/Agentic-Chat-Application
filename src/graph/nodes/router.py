from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from src.graph.state import AgentState
from src.config import OPENAI_API_KEY

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: Literal["vector_store", "general_chat"] = Field(
        ...,
        description="Given a user question choose to route it to vector_store or general_chat.",
    )

def route_question(state: AgentState):
    """
    Route question to web search or vectorstore.
    
    Args:
        state (dict): The current graph state
        
    Returns:
        str: Next node to call
    """
    print("---ROUTE QUESTION---")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    structured_llm_router = llm.with_structured_output(RouteQuery)
    
    system = """You are an expert at routing a user question to a vectorstore or general chat.
    The vectorstore contains documents related to 'SynergisticIT', 'JOPP', 'Job Placement Program', 'Java', 'Python', 'Data Science', 'AWS', 'MERN Stack' courses and 'Fees'.
    Use the vectorstore for questions on these topics.
    Use general_chat for greetings or general questions that might not need specific course documentation (if they passed guardrails).
    If the question is unclear, default to vector_store."""
    
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    
    question_router = route_prompt | structured_llm_router
    
    question = state["question"]
    source = question_router.invoke({"question": question})
    
    if source.datasource == "vector_store":
        print("---ROUTE QUERY TO VECTOR STORE---")
        return "vector_store"
    elif source.datasource == "general_chat":
        print("---ROUTE QUERY TO GENERAL CHAT---")
        return "general_chat"
