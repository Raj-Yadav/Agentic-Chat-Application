from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.graph.state import AgentState
from src.config import OPENAI_API_KEY

def rewrite_query(state: AgentState):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """
    print("---TRANSFORM QUERY---")
    question = state["question"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    
    msg = [
        ("system", """You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""),
        ("human", f"Here is the initial question: \n\n {question} \n Formulate an improved question."),
    ]
    
    grader_llm = llm | StrOutputParser()
    better_question = grader_llm.invoke(msg)
    
    print(f"---UPDATED QUESTION: {better_question}---")
    return {"question": better_question, "loop_step": state.get("loop_step", 0) + 1}
