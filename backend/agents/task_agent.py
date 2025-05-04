import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import webbrowser

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Simple in-memory checkpointing
memory = MemorySaver()

# Asset paths
ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')
NOTES_FILE_PATH = os.path.join(ASSETS_FOLDER, "notes.txt")
JOB_LIST_PATH = os.path.join(ASSETS_FOLDER, "jobs.xls")
WORKOUT_ROUTINE_PATH = os.path.join(ASSETS_FOLDER, "workout.txt")

# Open file helper
def open_file(file_type: str):
    """
    Opens the specified file based on its type.
    
    Args:
        file_type (str): The type of file to open, either "notes", "job_list", or "workout".
    
    Returns:
        dict: A dictionary containing the result of the file open operation.
    """
    print(f"Attempting to open file of type: {file_type}")
    file_paths = {
        "notes": NOTES_FILE_PATH,
        "job_list": JOB_LIST_PATH,
        "workout": WORKOUT_ROUTINE_PATH,
        "study": "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OneNote.lnk"
    }
    
    file_path = file_paths.get(file_type.lower())
    print("TRYING TO OPEN FILE:", file_path)
    if not file_path or not os.path.exists(file_path):
        return {"error": f"{file_type.capitalize()} file not found."}
    
    try:
        os.startfile(file_path)
        return {"file_content": f"{file_type.capitalize()} file opened successfully."}
    except Exception as e:
        return {"error": f"Failed to open {file_type} file. Error: {str(e)}"}

# Task-related tools
def handle_task_category(category: str):
    """
    Handles a specific category of task by invoking appropriate actions.
    
    Args:
        category (str): The category of task (e.g., 'relaxing videos', 'job applications', etc.)
    
    Returns:
        dict: The result of the task action.
    """
    print(f"Handling task for category: {category}")
    
    if category == "relaxing videos":
        webbrowser.open("https://www.youtube.com/watch?v=tr2qv6_aDeo")
        return {"action": "Searching for relaxing videos..."}
    elif category == "job applications":
        webbrowser.open("https://www.linkedin.com/feed/")
        return open_file("job_list")#{"action": "Opening LinkedIn and job list..."}
    elif category == "study material":
        return open_file("study")
        #return {"action": "Displaying study material..."}
    elif category == "motivational content":
        webbrowser.open("https://www.youtube.com/watch?v=TgHcTailbao")
        return {"action": "Fetching motivational content..."}
    elif category == "workout routine":
        print("Opening workout routine file...")
        return open_file("workout")
    elif category == "notes file":
        print("Opening notes file...")
        return open_file("notes")
    else:
        return {"error": "Unrecognized category."}

class TaskAgent:
    SYSTEM_INSTRUCTION = (
        "You are a task management assistant. You will categorize input prompts and execute tasks like opening files, "
        "searching for videos, or providing study materials based on the user's request."
    )

    CATEGORIES = [
        "relaxing videos", "job applications", "study material", 
        "motivational content", "workout routine", "notes file"
    ]

    def __init__(self):
        # Initialize model and tools
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
        self.tools = [handle_task_category]
        self.graph = create_react_agent(
            self.model, tools=self.tools, checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION
        )

    def invoke(self, query: str, sessionId: str):
        """
        Classifies the input query and executes the corresponding task based on the category.
        
        Args:
            query (str): The user query to be processed by the task agent.
            sessionId (str): The session identifier to keep track of the user's interaction.
        
        Returns:
            dict: A dictionary containing the task completion status and response content.
        """
        print(f"Invoking agent with query: {query} and sessionId: {sessionId}")
        
        # Classify input query into one of the categories
        category = self.classify_input(query)
        result = handle_task_category(category)
        return result

    def classify_input(self, query: str):
        """
        Classifies the user's query into one of the predefined categories.
        
        Args:
            query (str): The user query to be classified.
        
        Returns:
            str: The category that matches the query most closely.
        """
        # Simple keyword-based classification (you can replace this with a more advanced classifier if needed)
        if any(keyword in query.lower() for keyword in ["relax", "calm", "meditation", "chill"]):
            return "relaxing videos"
        elif any(keyword in query.lower() for keyword in ["job", "application", "linkedin", "resume"]):
            return "job applications"
        elif any(keyword in query.lower() for keyword in ["study", "material", "notes", "revision"]):
            return "study material"
        elif any(keyword in query.lower() for keyword in ["motivation", "inspire", "encourage", "push"]):
            return "motivational content"
        elif any(keyword in query.lower() for keyword in ["workout", "exercise", "fitness", "routine"]):
            return "workout routine"
        elif any(keyword in query.lower() for keyword in ["notes", "file", "documents"]):
            return "notes file"
        else:
            return "notes file"  # Default category
