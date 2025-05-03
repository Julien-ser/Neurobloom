from agents.journal_agent import JournalAgent
from agents.emotion_agent import EmotionAgent
from agents.task_agent import TaskAgent
import os

'''agent = EmotionAgent()
session_id = "emotion-session-001"
image_path = "image.png"

response = agent.invoke(image_path, session_id)
print(response)
# Initialize the TaskAgent
task_agent = TaskAgent()

# Sample call to open the "notes" file and check the response
query = "open my notes"
session_id = "session_1234"  # A unique session ID for your request

# Invoke the agent with the query
response = task_agent.invoke(query, session_id)

# Print out the response
print(response)'''

agent = JournalAgent()
print(agent.invoke("I've been feeling overwhelmed lately.", "test-session"))
