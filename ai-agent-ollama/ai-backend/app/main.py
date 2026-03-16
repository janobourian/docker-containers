from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

# Configuration from environment variables
# Note: ai-model is the name of the service in compose.yml
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ai-model:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder-v2:16b")

@app.get("/")
async def read_root():
    return {"message": "AI Agent Backend is running", "ollama_url": OLLAMA_URL, "model": OLLAMA_MODEL}

@app.get("/health")
async def health_check():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            return {"status": "ok", "ollama": "connected", "details": response.json()}
        except Exception as e:
            return {"status": "error", "ollama": "disconnected", "error": str(e)}

@app.post("/ask")
async def ask_question(request: Request):
    body = await request.json()
    prompt = body.get("message", "")
    
    if not prompt or prompt == "ping":
        return {"answer": "pong"}

    print(f"Asking {OLLAMA_MODEL} at {OLLAMA_URL}...")
    async with httpx.AsyncClient() as client:
        try:
            # We use the /api/generate endpoint of Ollama
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300.0 # Increased timeout for large models
            )
            
            if response.status_code == 404:
                return {"answer": f"Error: Model '{OLLAMA_MODEL}' not found. It might still be pulling in the background. Please wait a few minutes and try again."}
            
            response.raise_for_status()
            result = response.json()
            return {"answer": result.get("response", "I'm sorry, I couldn't generate a response.")}
        except httpx.ConnectError:
            return {"answer": "Error: Could not connect to the AI model container. Is it running?"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"answer": f"Error 404: Model '{OLLAMA_MODEL}' not found or endpoint invalid. Check if the model is fully pulled."}
            return {"answer": f"HTTP Error: {str(e)}"}
        except Exception as e:
            return {"answer": f"Error: {str(e)}"}
