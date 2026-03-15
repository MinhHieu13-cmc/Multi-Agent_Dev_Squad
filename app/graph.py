from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
# Force uvicorn reload 2

from app.state import AgentState
from app.nodes.lead import lead_node
from app.nodes.coder import coder_node
from app.nodes.qa import qa_node, route_qa
from app.nodes.saver import saver_node

def build_graph():
    """
    Constructs the StateGraph for the Dev Squad flow.
    Lead -> Coder -> QA -> (Conditional: End or Coder)
    """
    # 1. Initialize the StateGraph with our TypedDict
    builder = StateGraph(AgentState)
    
    # 2. Add the agent nodes
    builder.add_node("lead", lead_node)
    builder.add_node("coder", coder_node)
    builder.add_node("qa", qa_node)
    builder.add_node("saver", saver_node)
    
    # 3. Define the edges and flow
    builder.set_entry_point("lead")
    builder.add_edge("lead", "coder")
    builder.add_edge("coder", "qa")
    
    # Conditional edge from QA
    builder.add_conditional_edges(
        "qa",
        route_qa,
        {
            "coder": "coder", # Loop back
            "saver": "saver"  # Save and finish
        }
    )
    
    # 5. Connect saver to end
    builder.add_edge("saver", END)
    
    # 4. Setup state persistence (SQLite Checkpointer)
    # Using checkpointer natively supports graph-based state saving and resuming
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    # Compile the graph
    app = builder.compile(checkpointer=memory)
    
    return app

# Expose a compiled graph instance
app_graph = build_graph()
