from fastapi import FastAPI, Request
from app.ai_agent.chat import chat_with_gpt4o
app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Compose Backend!"}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    return await chat_with_gpt4o(body.get("message", ""))