import docker
import tempfile
import os

def run_code_in_sandbox(code: str) -> dict:
    """
    Executes the provided Python code in an isolated Docker container.
    Returns a dictionary containing 'logs' and 'success' boolean.
    """
    client = docker.from_env()
    
    # Create a temporary file containing the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    target_path = "/app/script.py"

    try:
        # Run the container using python:3.10-slim image
        # Mount the temporary file into the container
        container = client.containers.run(
            image="python:3.10-slim",
            command=f"python {target_path}",
            volumes={temp_file_path: {'bind': target_path, 'mode': 'ro'}},
            remove=False,
            detach=True,
            mem_limit='128m',  # Security: limit memory
            network_disabled=True # Security: disable network access if possible or needed
        )
        
        # Wait for the container to finish
        result = container.wait(timeout=10)
        logs = container.logs().decode('utf-8')
        
        status_code = result.get('StatusCode', 1)
        container.remove(force=True)
        
        return {
            "success": status_code == 0,
            "logs": logs
        }
        
    except docker.errors.ContainerError as e:
        return {
            "success": False,
            "logs": f"Container Error: {e.stderr.decode('utf-8') if e.stderr else 'Unknown Error'}"
        }
    except Exception as e:
        return {
            "success": False,
            "logs": f"Execution Error: {str(e)}"
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
