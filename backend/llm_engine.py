import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def generate_ai_reply(user_text, emotion, memory_context=""):
    prompt = f"""
You are Emily, an emotional AI assistant.

Emotion: {emotion}
Memory:
{memory_context}

User: {user_text}
Emily:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        return "Sorry, I'm having trouble responding."

    return response.json()["response"].strip()
