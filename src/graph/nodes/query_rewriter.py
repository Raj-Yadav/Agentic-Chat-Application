"""
Query Rewriter Module.
Transforms semantic intent into an optimized search query.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.graph.state import AgentState
from src.config import OPENAI_API_KEY
from langsmith import traceable

@traceable
def rewrite_query(state: AgentState) -> Dict[str, Any]:
    """
    Transform the query to produce a better question.

    Args:
        state (AgentState): The current graph state.

    Returns:
        Dict[str, Any]: Updates 'question' key with a re-phrased question and increments 'loop_step'.
    """
    print("---TRANSFORM QUERY---")
    question = state["question"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    
    msg = [
        ("system", """Rewrite user input into specific semantic questions for vector search.

    **Context**:
    - ISA -> Income Share Agreement.
    - JOPP -> Job Placement.
    - Money back -> Refund/Deposit.
    - Fake/Scam -> Legitimacy/Reviews.
    
    **Examples**:
    - "cost?" -> "What is the tuition cost and fee structure?"
    - "java tools" -> "What technologies are covered in Java Full Stack?"
    - "fake?" -> "Is SynergisticIT legitimate? Show reviews."
    - "money back?" -> "What is the refund policy for the deposit?"
    - "how long and price" -> "What is the duration and tuition cost?"

    Return ONLY the rewritten question. No preamble.
    """),
        ("human", f"Question: {question}"),
    ]
    
    grader_llm = llm | StrOutputParser()
    better_question = grader_llm.invoke(msg)
    
    print(f"---UPDATED QUESTION: {better_question}---")
    return {"question": better_question, "loop_step": state.get("loop_step", 0) + 1}
