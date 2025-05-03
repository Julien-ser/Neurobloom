from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Simple in-memory checkpointing
memory = MemorySaver()

# Asset paths
ASSETS_FOLDER = "assets"
NOTES_FILE_PATH = os.path.join(ASSETS_FOLDER, "Notes.txt")
JOB_LIST_PATH = os.path.join(ASSETS_FOLDER, "Job_List.csv")

# Open file helper
def open_file(file_type: str):
    """
    Opens the specified file based on its type.
    
    Args:
        file_type (str): The type of file to open, either "notes" or "job_list".
    
    Returns:
        dict: A dictionary containing the result of the file open operation.
    """
    print(f"Attempting to open file of type: {file_type}")
    file_paths = {
        "notes": NOTES_FILE_PATH,
        "job_list": JOB_LIST_PATH
    }
    
    file_path = file_paths.get(file_type.lower())
    if not file_path or not os.path.exists(file_path):
        return {"error": f"{file_type.capitalize()} file not found."}
    
    try:
        os.startfile(file_path)
        return {"file_content": f"{file_type.capitalize()} file opened successfully."}
    except Exception as e:
        return {"error": f"Failed to open {file_type} file. Error: {str(e)}"}

# Task-related tools
def open_task(task_id: str):
    """
    Opens the specified task based on its task ID.
    
    Args:
        task_id (str): The ID of the task to open.
    
    Returns:
        dict: A dictionary containing the details of the opened task.
    """
    print(f"Opening task with ID: {task_id}")
    return {"task_details": f"Opening task {task_id}. [Details would go here.]"}

def list_tasks():
    """
    Lists all available tasks.
    
    Returns:
        dict: A dictionary containing a list of available tasks.
    """
    print("Listing all tasks")
    return {"tasks": ["Task 1", "Task 2", "Task 3"]}

class TaskAgent:
    SYSTEM_INSTRUCTION = (
        "You are a task management assistant. You can open tasks, list tasks, open files, and list files."
    )

    def __init__(self):
        # Initialize model and tools
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
        self.tools = [open_task, list_tasks, open_file]

        # Create the React agent with the provided tools
        self.graph = create_react_agent(
            self.model, tools=self.tools, checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION
        )

    def invoke(self, query: str, sessionId: str) -> Dict[str, Any]:
        """
        Invokes the task agent to process a query and returns a structured response.
        
        Args:
            query (str): The user query to be processed by the task agent.
            sessionId (str): The session identifier to keep track of the user's interaction.
        
        Returns:
            dict: A dictionary containing the task completion status and response content.
        """
        print(f"Invoking agent with query: {query} and sessionId: {sessionId}")
        config = {"configurable": {"thread_id": sessionId}}
        result = self.graph.invoke({"messages": [("user", query)]}, config)
        print(f"Result of invoke: {result}")
        return self.get_agent_response(config)

    def get_agent_response(self, config):
        """
        Extracts the response from the agent's state.
        
        Args:
            config (dict): The configuration passed to the agent for retrieving the state.
        
        Returns:
            dict: The structured response containing task completion status and message.
        """
        print(f"Getting agent response for config: {config}")
        current_state = self.graph.get_state(config)
        print(f"Current state: {current_state}")
        structured_response = current_state.values.get('structured_response', {})
        
        return {
            "is_task_complete": structured_response.get('status') == "completed",
            "require_user_input": structured_response.get('status') == "input_required",
            "content": structured_response.get('message', "I couldn't complete your request.")
        }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

# Example of usage
if __name__ == "__main__":
    agent = TaskAgent()
    response = agent.invoke("List tasks", "session_1")
    print(response)

    response = agent.invoke("Open task 1", "session_1")
    print(response)

    response = agent.invoke("Open the Notes file", "session_1")
    print(response)

    response = agent.invoke("Open the Job List file", "session_1")
    print(response)
