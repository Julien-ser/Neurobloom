import time

# Assuming TaskAgent is already imported
from agents.task_agent import TaskAgent  # Adjust this import path as necessary

# Create an instance of TaskAgent
agent = TaskAgent()

response = agent.invoke("Open the Notes file", "session_1")
print(response)
