from fastapi import FastAPI, Request
from app.ask.ask import ask_model
import os

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Compose Backend!"}

@app.post("/ask")
async def ask_question(request: Request):
    body = await request.json()
    answer = await ask_model(body.get("message", ""))
    return {"answer": answer}