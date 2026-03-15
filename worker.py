from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from dotenv import load_dotenv

from app.graph import app_graph
from langgraph.types import Command

load_dotenv()

app = FastAPI(title="Multi-Agent Dev Squad Worker API")

class TaskRequest(BaseModel):
    prompt: str
    thread_id: Optional[str] = None

class TaskResponse(BaseModel):
    thread_id: str
    status: str

def run_agent_graph(task_prompt: str, thread_id: str):
    """
    Executes the Dev Squad graph in the background.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if this thread already has an active state we should resume
    # The checkpointer handles persistence, so if this thread exists, 
    # invoke will resume from the last node.
    initial_state = {
        "task": task_prompt,
        "plan": "",
        "code": "",
        "execution_logs": "",
        "qa_status": "pending",
        "messages": [],
        "iterations": 0
    }
    
    try:
        # LangGraph invoke will run the graph synchronously here.
        # In a real heavy production setup, this might be handled via a Celery worker.
        app_graph.invoke(initial_state, config=config)
    except Exception as e:
        print(f"Error during graph execution for thread {thread_id}: {e}")

@app.post("/task", response_model=TaskResponse)
async def submit_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Submit a high-level task for the Dev Squad.
    Returns a thread_id that can be used to check status.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    
    # Run the graph in a background task
    background_tasks.add_task(run_agent_graph, request.prompt, thread_id)
    
    return TaskResponse(thread_id=thread_id, status="accepted")

@app.get("/task/{thread_id}")
async def get_task_status(thread_id: str):
    """
    Check the status and current state of a task by thread_id.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state = app_graph.get_state(config)
    
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="Task not found")
        
    values = state.values
    return {
        "thread_id": thread_id,
        "qa_status": values.get("qa_status"),
        "iterations": values.get("iterations"),
        "code": values.get("code"),
        "execution_logs": values.get("execution_logs")
    }
