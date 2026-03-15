from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.state import AgentState

lead_prompt = """You are the Lead AI Architect. Your job is to take a high-level user request and break it down into a clear, actionable plan for a Software Engineer (Coder).
The output should only contain the structured plan, without any conversational filler.
"""

def lead_node(state: AgentState):
    """
    Lead agent node: Analyzes the task and creates a plan.
    """
    print("---LEAD AGENT: Planning Task---")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    messages = [
        SystemMessage(content=lead_prompt),
        HumanMessage(content=f"Task: {state['task']}")
    ]
    
    response = llm.invoke(messages)
    
    return {
        "plan": response.content,
        "messages": [response],
        "iterations": 0,
        "qa_status": "pending",
        "code": "",
        "execution_logs": ""
    }
