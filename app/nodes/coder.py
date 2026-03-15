from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.state import AgentState
import re

coder_prompt = """You are an Expert Software Engineer. 
Your job is to write Python code based on the provided plan.
If you receive feedback from the QA Verifier (execution logs/errors), you MUST fix the errors in your code.

OUTPUT RULES:
- You must output ONLY valid, executable Python code.
- Do not include markdown formatting like ```python or ```. 
- Do not include conversational text or explanations.
- Just the raw code.
"""

def extract_code(text: str) -> str:
    """Helper to strip markdown code blocks if the LLM includes them."""
    # Remove leading ```python or ``` and trailing ```
    stripped = re.sub(r"^```python\n", "", text, flags=re.IGNORECASE)
    stripped = re.sub(r"^```\n", "", stripped)
    stripped = re.sub(r"```$", "", stripped)
    return stripped.strip()

def coder_node(state: AgentState):
    """
    Coder agent node: Writes or fixes Python code based on the plan and QA logs.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    content = f"Plan:\n{state['plan']}\n\n"
    
    if state.get("execution_logs") and state.get("qa_status") == "failed":
        content += f"Previous Code:\n{state['code']}\n\n"
        content += f"QA Execution Logs (Error):\n{state['execution_logs']}\n\n"
        content += "Please fix the code based on the errors above."
    else:
        content += "Please write the initial code for this plan."

    messages = [
        SystemMessage(content=coder_prompt),
        HumanMessage(content=content)
    ]
    
    response = llm.invoke(messages)
    
    raw_code = response.content
    clean_code = extract_code(raw_code)
    
    # Increment iteration count
    iterations = state.get("iterations", 0) + 1
    
    return {
        "code": clean_code,
        "messages": [response],
        "iterations": iterations
    }
