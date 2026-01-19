from typing import List, TypedDict

class AgentState(TypedDict):
    """
    The state of our agent.
    """
    question: str
    documents: List[str]
    generation: str
    guardrail_status: str
    loop_step: int
