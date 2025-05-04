from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from typing import Dict, Any, AsyncIterable
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Simple in-memory checkpointing
memory = MemorySaver()

@tool
def write_journal_entry(reflection: str) -> str:
    """Use Gemini to turn a user reflection into a thoughtful, dated, and expressive journal entry."""
    reflection = reflection.strip()
    if not reflection or len(reflection.split()) <= 3:
        return "Your reflection seems a little short — could you tell me more before we write the journal entry?"

    today = datetime.now().strftime("%A, %B %d, %Y")

    # Create a local Gemini model instance
    tmodel = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # Prompt to get a natural journal-style entry
    prompt = (
        "Convert this reflection into a thoughtful first-person journal entry. "
        "Avoid adding a greeting or date. Be natural, expressive, and introspective.\n\n"
        f"Reflection: {reflection}\n\n"
        "Journal Entry:"
    )

    response = tmodel.invoke(prompt)
    body = response.content.strip()

    entry = (
        f"{today}\n\n"
        "Dear Journal,\n\n"
        f"{body}\n\n"
        "Until next time,\n"
        "—Me"
    )

    print("Generated Entry:", entry)  # TEMP debug
    return entry


class ResponseFormat(BaseModel):
    status: str = "input_required"  # Could be "input_required", "completed", or "error"
    message: str

def is_reflection_valid(reflection: str) -> bool:
    """Check if the reflection is meaningful enough to journal."""
    reflection = reflection.strip()
    # Too short or common vague responses
    if len(reflection) < 10:
        return False
    vague_keywords = {"ok", "good", "fine", "yes", "no", "maybe", "hello", "idk", "lol", "ugh", "meh"}
    return not (reflection.lower() in vague_keywords or len(reflection.split()) <= 2)


class JournalAgent:
    SYSTEM_INSTRUCTION = (
        "You are a journaling assistant that always converts user reflections into thoughtful, dated journal entries using the `write_journal_entry` tool. "
        "If the user input is vague, too short (under 10 characters), or only 1–2 words, respond with a warm clarification request. "
        "Never say just 'ok'. Never respond with a generic completion if the reflection is empty or unclear. "
        "If the input is valid, return the journal entry using `write_journal_entry`, then wrap it in a ResponseFormat with `status='completed'` and `message=<entry>`. "
        "Always include the current date and be thoughtful and calm in tone."
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
        if not is_reflection_valid(query):
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "Can you tell me a bit more? A few words isn’t quite enough to reflect on."
            }

        config = {"configurable": {"thread_id": sessionId}}
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

