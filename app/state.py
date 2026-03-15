from typing import TypedDict, Annotated, List, Any
import operator
from langchain_core.messages import BaseMessage


def add_messages(left: list, right: list):
    """Append new messages to the existing list."""
    return left + right


class AgentState(TypedDict):
    """
    Represents the shared memory (state) of the Multi-Agent Dev Squad.
    """
    # High-level user prompt
    task: str
    
    # The Lead's breakdown of the task
    plan: str
    
    # The current code written by the Coder
    code: str
    
    # Execution logs from the QA's sandbox run
    execution_logs: str
    
    # Status of QA assessment: "pending", "passed", or "failed"
    qa_status: str
    
    # Interaction history between agents
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Number of iterations the Coder has tried to fix the code
    iterations: int
