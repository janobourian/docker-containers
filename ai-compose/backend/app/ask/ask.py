import httpx
from app.utils import MODEL_URL

async def ask_model(message: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MODEL_URL}/chat",
            json={"message": message},
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "No answer")