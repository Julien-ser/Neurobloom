'''from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from typing import Literal, AsyncIterable, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Simple in-memory checkpointing
memory = MemorySaver()

@tool
def write_journal_entry(reflection: str):
    """Summarize the user's reflection into a concise journal entry."""
    return {
        "journal_entry": f"Today, you reflected on: {reflection}. Remember to take care of yourself and stay consistent."
    }

class ResponseFormat(BaseModel):
    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str

class JournalAgent:

    SYSTEM_INSTRUCTION = (
        "You are a journaling assistant that helps users reflect on their day or emotions. "
        "Use the `write_journal_entry` tool to convert reflections into short journal entries. "
        "Be empathetic. If the user hasn't provided enough input, ask them a follow-up question. "
        "Use `completed` only when a meaningful journal entry is created."
    )

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
        self.tools = [write_journal_entry]

        self.graph = create_react_agent(
            self.model, tools=self.tools, checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION, response_format=ResponseFormat
        )

    def invoke(self, query: str, sessionId: str) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": sessionId}}
        self.graph.invoke({"messages": [("user", query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query: str, sessionId: str) -> AsyncIterable[Dict[str, Any]]:
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}}

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {"is_task_complete": False, "require_user_input": False, "content": "Creating your journal entry..."}
            elif isinstance(message, ToolMessage):
                yield {"is_task_complete": False, "require_user_input": False, "content": "Finishing up your entry..."}

        yield self.get_agent_response(config)

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
            "content": "Something went wrong creating your journal entry."
        }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]'''
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from typing import Dict, Any, AsyncIterable
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Simple in-memory checkpointing
memory = MemorySaver()

@tool
def write_journal_entry(reflection: str) -> Dict[str, str]:
    """Tool to generate a journal entry from the user's reflection."""
    return {
        "journal_entry": f"Today, you reflected on: {reflection}. Remember to take care of yourself and stay consistent."
    }

class ResponseFormat(BaseModel):
    status: str = "input_required"  # Could be "input_required", "completed", or "error"
    message: str

class JournalAgent:
    SYSTEM_INSTRUCTION = (
        "You are a journaling assistant that helps users reflect on their day or emotions. "
        "Use the `write_journal_entry` tool to convert reflections into short journal entries. "
        "Be empathetic. If the user hasn't provided enough input, ask them a follow-up question. "
        "Use `completed` only when a meaningful journal entry is created."
    )

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
        self.tools = [write_journal_entry]
        self.graph = create_react_agent(
            self.model, tools=self.tools, checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION, response_format=ResponseFormat
        )

    def invoke(self, query: str, sessionId: str) -> Dict[str, Any]:
        """Process journal request, generate journal entry, and return response."""
        config = {"configurable": {"thread_id": sessionId}}
        # Trigger the agent's response based on user's input
        self.graph.invoke({"messages": [("user", query)]}, config)
        return self._get_agent_response(config)

    async def stream(self, query: str, sessionId: str) -> AsyncIterable[Dict[str, Any]]:
        """Stream the journal creation process asynchronously."""
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}}

        # Stream the agent's responses while processing
        async for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if isinstance(message, AIMessage) and message.tool_calls:
                yield {"is_task_complete": False, "require_user_input": False, "content": "Creating your journal entry..."}
            elif isinstance(message, ToolMessage):
                yield {"is_task_complete": False, "require_user_input": False, "content": "Finishing up your entry..."}

        # Final response once journal entry is created
        yield self._get_agent_response(config)

    def _get_agent_response(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to extract structured response from the agent."""
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
            "content": "Something went wrong creating your journal entry."
        }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

