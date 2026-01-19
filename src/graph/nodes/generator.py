from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.graph.state import AgentState
from src.config import OPENAI_API_KEY

def generate(state: AgentState):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    
    system = """You are a specialized "SynergisticIT counselor" — professional, encouraging, and accurate.
    Use the following pieces of retrieved context to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    If you cannot answer the question, or if you say "I don't know", you MUST append the following message to your response:
    "\nFor more information about program offered by synergisticIT, you should contact us at: https://www.synergisticit.com/contact-us/"
    
    Keep the answer concise."""
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Context: {context} \n\n Question: {question}"),
        ]
    )
    
    rag_chain = prompt | llm | StrOutputParser()
    
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"generation": generation}
