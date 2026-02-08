"""
Grader Module.
Evaluates the relevance of retrieved documents to the user question.
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from src.graph.state import AgentState
from src.config import OPENAI_API_KEY
from langsmith import traceable

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )
    explanation: str = Field(
        description="Brief explanation of why the document is relevant or not"
    )

@traceable
def grade_documents(state: AgentState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (AgentState): The current graph state.

    Returns:
        Dict[str, Any]: Updates 'documents' key with only filtered relevant documents.
    """
    print("---CHECK RELEVANCE---")
    question = state["question"]
    documents = state["documents"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    structured_llm_grader = llm.with_structured_output(GradeDocuments)
    
    system = """Grade relevance of document to question.

    **Rules**:
    1. Check if document contains *evidence* for the question.
    2. relevant ('yes'): Quote specific supporting sentence(s).
    3. irrelevant ('no'): Explain why (e.g., "Topic mismatch").
    """
    
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )
    
    retrieval_grader = grade_prompt | structured_llm_grader
    
    filtered_docs: List[Document] = []
    yes_count = 0
    total_count = len(documents)
    
    for d in documents:
        try:
            score = retrieval_grader.invoke({"question": question, "document": d.page_content})
            grade = score.binary_score
            
            if grade == "yes":
                filtered_docs.append(d)
                yes_count += 1
            else:
                # Log what it thought was missing
                pass
        except Exception as e:
            print(f"  [ERROR] Grader failed for document: {d.page_content[:50]}... Error: {e}")
            continue
            
    relevance_score = f"{yes_count}/{total_count}"
    print(f"---RELEVANCE SCORE: {relevance_score}---")
    
    return {"documents": filtered_docs, "question": question, "relevance_score": relevance_score}
