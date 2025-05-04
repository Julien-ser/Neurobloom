# backend/main.py
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from agents.emotion_agent import EmotionAgent
from agents.journal_agent import JournalAgent
from agents.task_agent import TaskAgent

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allow frontend dev environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://localhost:5173"] for stricter CORS handling
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent instances
emotion_agent = EmotionAgent()
journal_agent = JournalAgent()
task_agent = TaskAgent()

@app.post("/emotion/upload")
async def upload_image(image: UploadFile = File(...), sessionId: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, f"{sessionId}.jpg")
    with open(file_path, "wb") as f:
        f.write(await image.read())

    emotion = emotion_agent.invoke(file_path, sessionId=sessionId)  # Replace with your real logic
    print("Emotion detected: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(emotion)
    print("Emotion detected: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    return JSONResponse({"emotion": emotion})

@app.post("/agent/journal")
async def handle_journal(payload: dict):
    query = payload.get("query")
    sessionId = payload.get("sessionId")
    result = journal_agent.invoke(query, sessionId=sessionId)
    print("Journal agent result: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(result)
    print("Journal agent result: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    return JSONResponse({"response": result})

@app.post("/agent/task")
async def handle_task(payload: dict):
    query = payload.get("query")
    sessionId = payload.get("sessionId")
    result = task_agent.invoke(query, sessionId=sessionId)
    return JSONResponse({"response": result})
