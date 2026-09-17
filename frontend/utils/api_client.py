import os

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def send_message(message: str, history: list) -> tuple[str, list]:
    """
    Sends a message to the FastAPI backend and returns (response_text, tools_used).
    """
    try:
        payload = {
            "message": message,
            "history": [
                {"role": m["role"], "content": m["content"]}
                for m in history
            ],
        }
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response"), data.get("tools_used", [])

    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Cannot connect to the backend. Make sure FastAPI is running on port 8000.",
            [],
        )
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. The agent is taking too long — please try again.", []
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}", []