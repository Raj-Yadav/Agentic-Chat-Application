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
        ("system", """You are a domain-expert question re-writer for SynergisticIT (a career acceleration program). 
    Your goal is to convert vague or short user input into a specific, semantic question optimized for vector search.

    **Domain Context**:
    - "ISA" -> Income Share Agreement (financial contract).
    - "JOPP" -> Job Placement Program.
    - "Java" -> Java Full Stack Track.
    - "Python" -> Data Science / Machine Learning Track.
    - "Money back" -> Refund policy / Deposit refund.
    - "Fake/Scam" -> Legitimacy / Trustworthiness / Reviews.
    - "Cost/Fee" -> Tuition profile / Payment options.

    **Examples**:
    - Input: "cost?" -> Output: "What is the tuition cost and fee structure for the program?"
    - Input: "java tools" -> Output: "What specific technologies and tools are covered in the Java Full Stack curriculum?"
    - Input: "fake?" -> Output: "Is SynergisticIT a legitimate company or a scam? show me reviews."
    - Input: "money back?" -> Output: "What is the refund policy for the security deposit?"

    Return ONLY the rewritten question string. Do not add any preamble."""),
        ("human", f"Here is the initial question: \n\n {question} \n Formulate an improved question."),
    ]
    
    grader_llm = llm | StrOutputParser()
    better_question = grader_llm.invoke(msg)
    
    print(f"---UPDATED QUESTION: {better_question}---")
    return {"question": better_question, "loop_step": state.get("loop_step", 0) + 1}
