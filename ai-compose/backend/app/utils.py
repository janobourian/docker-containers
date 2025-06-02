import os

MODEL_HOST = os.getenv("MODEL_HOST", "ai-model")
MODEL_PORT = os.getenv("MODEL_PORT", "8001")
MODEL_URL = f"http://{MODEL_HOST}:{MODEL_PORT}"
