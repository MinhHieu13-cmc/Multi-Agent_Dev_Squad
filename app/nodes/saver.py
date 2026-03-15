import os
from app.state import AgentState
from langchain_core.runnables import RunnableConfig

def saver_node(state: AgentState, config: RunnableConfig):
    """
    Saves the final passed code to a local directory.
    """
    code = state.get("code", "")
    # thread_id is passed in the config by worker.py
    thread_id = config.get("configurable", {}).get("thread_id", "unknown_task")
    
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    file_path = f"outputs/{thread_id}.py"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
        
    print(f"---SAVER AGENT: Saved code to {file_path}---")
    
    return {}
