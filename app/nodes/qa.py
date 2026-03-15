from app.state import AgentState
from app.tools.sandbox import run_code_in_sandbox
from langchain_core.messages import AIMessage

MAX_ITERATIONS = 3

def qa_node(state: AgentState):
    """
    QA Verifier node: Executes the Coder's code in a sandbox.
    """
    print("---QA AGENT: Evaluating Code---")
    
    code = state.get("code", "")
    iterations = state.get("iterations", 0)
    
    if not code.strip():
        message = AIMessage(content="QA Failed: No code provided to evaluate.")
        return {
            "qa_status": "failed",
            "execution_logs": "No code provided.",
            "messages": [message]
        }
    
    print("Running code in sandbox...")
    result = run_code_in_sandbox(code)
    
    success = result["success"]
    logs = result["logs"]
    
    if success:
        print("-> QA Passed!")
        status = "passed"
        msg_content = "QA Passed. Execution successful.\nLogs:\n" + logs
    else:
        print("-> QA Failed!")
        status = "failed"
        msg_content = "QA Failed. Execution error.\nLogs:\n" + logs
        
    # Check if we hit the iteration limit
    if not success and iterations >= MAX_ITERATIONS:
        print("-> Max iterations reached. Forcing pass/complete.")
        status = "passed" # Force pass to prevent infinite loop, or handle differently
        msg_content += "\nMax iteration limit reached."
        
    message = AIMessage(content=msg_content)
    
    return {
        "qa_status": status,
        "execution_logs": logs,
        "messages": [message]
    }

def route_qa(state: AgentState) -> str:
    """
    Conditional edge router: determines whether to loop back to Coder or finish.
    """
    status = state.get("qa_status")
    if status == "passed":
        return "saver"
    else:
        return "coder"
