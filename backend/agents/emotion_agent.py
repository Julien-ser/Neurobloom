from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from typing import Literal, AsyncIterable, Dict, Any
from dotenv import load_dotenv
import os
from deepface import DeepFace

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Simple in-memory checkpointing
memory = MemorySaver()

# Emotion Detection tool using DeepFace
@tool
def detect_emotion(image_path: str):
    """Detect emotion from the image using DeepFace."""
    analysis = DeepFace.analyze(image_path, actions=['emotion'])
    dominant_emotion = analysis[0]['dominant_emotion']
    print("**************************************DOM EMOTION**************************************")
    print(dominant_emotion)
    print("**************************************DOM EMOTION**************************************")
    return {
        "emotion": dominant_emotion
    }

class ResponseFormat(BaseModel):
    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str

class EmotionAgent:

    SYSTEM_INSTRUCTION = (
        "You are an emotion assistant that detects the user's emotional state from images. "
        "If the user provides an image, you will detect the dominant emotion and respond empathetically. "
        "Ask follow-up questions if necessary to help the user process their emotions."
    )

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
        self.tools = [detect_emotion]

        self.graph = create_react_agent(
            self.model, tools=self.tools, checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION, response_format=ResponseFormat
        )

    def invoke(self, image_path: str, sessionId: str) -> Dict[str, Any]:
        # Detect emotion from the image
        emotion_response = detect_emotion(image_path)
        emotion = emotion_response["emotion"]
        
        # Generate suggested action based on emotion
        suggested_action = self.get_suggested_action(emotion)
        
        # Generate journal content based on the emotion
        journal_content = self.get_journal_content(emotion)
        
        # Standardized response format
        return {
            "response": {
                "message": f"Detected emotion: {emotion}",
                "data": {
                    "emotion": emotion,
                    "suggested_action": suggested_action,
                    "journal_content": journal_content
                },
                "status": "completed"
            }
        }

    def get_journal_content(self, emotion: str) -> str:
        """Generate journal content prompt based on the detected emotion."""
        # Normalize the emotion string to lowercase for case-insensitive comparison
        emotion = emotion.lower()

        if emotion == "happy":
            return "Capture what made you smile today."
        elif emotion == "sad":
            return "Write about what's weighing on you and how you're coping."
        elif emotion == "angry":
            return "Explore what sparked your anger and how it affected you."
        elif emotion == "surprise":
            return "Describe the moment that caught you off guard."
        elif emotion == "fear":
            return "Reflect on what’s making you anxious and what might ease it."
        elif emotion == "disgust":
            return "Journal about what bothered you and why it had that effect."
        else:
            return "Take a moment to write freely about how you're feeling."

    async def stream(self, image_path: str, sessionId: str) -> AsyncIterable[Dict[str, Any]]:
        # First, detect emotion from the image
        emotion_response = detect_emotion(image_path)
        emotion = emotion_response["emotion"]
        
        # Generate Suggested Action based on the emotion
        suggested_action = self.get_suggested_action(emotion)
        
        # Generate journal content based on the emotion
        journal_content = self.get_journal_content(emotion)
        
        # Formulate the response based on the detected emotion and suggested action
        query = f"User's detected emotion is: {emotion}. How can I help you process this emotion?"
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}}

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if isinstance(message, AIMessage) and message.tool_calls and len(message.tool_calls) > 0:
                yield {"is_task_complete": False, "require_user_input": False, "content": "Analyzing your emotion..."}
            elif isinstance(message, ToolMessage):
                yield {"is_task_complete": False, "require_user_input": False, "content": "Responding empathetically..."}

        # Get the agent's response after the analysis
        response = self.get_agent_response(config)
        
        # Yield the response with content, emotion, suggested action, and journal content
        yield {
            "content": response["content"],
            "emotion": emotion,
            "suggested_action": suggested_action,
            "journal_content": journal_content
        }


    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(structured_response, ResponseFormat):
            return {
                "is_task_complete": structured_response.status == "completed",
                "require_user_input": structured_response.status == "input_required",
                "content": structured_response.message
            }

        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "Something went wrong while processing your emotion."
        }

    def get_suggested_action(self, emotion: str) -> str:
        """Generate suggested action based on the detected emotion."""
        # Normalize the emotion string to lowercase for case-insensitive comparison
        emotion = emotion.lower()
        
        if emotion == "happy":
            return "Keep up the momentum!"
        elif emotion == "sad":
            return "Play a comforting video."
        elif emotion == "angry":
            return "Try a breathing exercise."
        elif emotion == "surprise":
            return "Log this moment."
        elif emotion == "fear":
            return "Take a moment to relax."
        elif emotion == "disgust":
            return "Take a deep breath and try to reset."
        else:
            return "Stay focused."




    SUPPORTED_CONTENT_TYPES = ["image", "image/jpeg", "image/png"]
