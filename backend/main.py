# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agents.emotion_agent import EmotionAgent
from agents.journal_agent import JournalAgent
from agents.task_agent import TaskAgent
from agents.rag_agent import RAGAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
emotion_agent = EmotionAgent()
journal_agent = JournalAgent()
task_agent = TaskAgent()
rag_agent = RAGAgent()

@app.post("/analyze-emotion")
async def analyze_emotion(request: Request):
    body = await request.json()
    return emotion_agent.invoke(body["text"], body["session_id"])

@app.post("/journal-entry")
async def journal_entry(request: Request):
    body = await request.json()
    return journal_agent.invoke(body["entry"], body["session_id"])

@app.post("/add-task")
async def add_task(request: Request):
    body = await request.json()
    return task_agent.invoke(body["task"], body["session_id"])

@app.post("/personal-query")
async def personal_query(request: Request):
    body = await request.json()
    return rag_agent.invoke(body["question"], body["session_id"])
