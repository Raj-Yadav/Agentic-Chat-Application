"""
Generator Module.
Generates the final answer using retrieved context and strict policy adherence rules.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.graph.state import AgentState
from src.config import OPENAI_API_KEY

def generate(state: AgentState) -> Dict[str, Any]:
    """
    Generate answer using only retrieved context.

    Args:
        state (AgentState): The current graph state.
    
    Returns:
        Dict[str, Any]: Updated state with 'generation'.
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state.get("documents", [])
    
    # Phase 6: Confidence-Aware Abstention
    if not documents:
        print("---DECISION: NO DOCUMENTS FOUND -> ABSTAIN---")
        return {"generation": "I don't have verified information about that yet."}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    
    # Phase 5: System Prompt Redesign & Policy Override
    system = """You are a specialized assistant for SynergisticIT. 
    You must ONLY use the provided context to answer the user's question.
    
    STRICT RULES:
    1. Answer strictly using the retrieved knowledge below.
    2. If partial information exists: provide the known portion and clearly state what is not confirmed.
    3. If the context is empty or irrelevant to the specific question, you MUST state: "I don't have verified information about that yet."
    4. **Policy Override**: If the context includes a section marked as 'Policy', it takes precedence over any other information (marketing, reviews, etc.).
    5. Do NOT use outside knowledge. Do NOT hallucinate.
    6. Keep the answer concise and professional.
    """
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Context: {context} \n\n Question: {question}"),
        ]
    )
    
    rag_chain = prompt | llm | StrOutputParser()
    
    try:
        generation = rag_chain.invoke({"context": documents, "question": question})
    except Exception as e:
        print(f"Error generation: {e}")
        generation = "I approached a technical issue and could not generate an answer."

    # Write to cache (Phase 15)
    from src.utils.cache import cache
    if generation and "I don't have verified information" not in generation:
        cache.set(question, generation)
        print(f"---CACHE UPDATE: Saved answer for '{question}'---")

    return {"generation": generation}
