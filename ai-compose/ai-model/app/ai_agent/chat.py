from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import time

load_dotenv(override=True)
gpt4o_chat = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=2000)


async def chat_with_gpt4o(message: str):
    start_time = time.perf_counter()

    response = gpt4o_chat.invoke([
        SystemMessage(content=(
            "You are a helpful AI assistant. Respond in **Markdown** format. "
            "Use bullet points, headings, and code blocks if needed. Keep responses concise."
        )),
        HumanMessage(content=message)
    ])

    return {
        "response": response.content,
        "time_taken": f"{time.perf_counter() - start_time:.2f} seconds",
    }
