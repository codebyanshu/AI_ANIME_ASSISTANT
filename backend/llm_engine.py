import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def generate_ai_reply(user_text, emotion, memory_context=""):
    prompt = f"""You are Emily, an emotional AI assistant. Emotion: {emotion} Memory: {memory_context} User: {user_text} Emily:"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        return "Sorry, I'm having trouble thinking right now."

    return response.json()["response"].strip()

# import requests
# from typing import Optional

# OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL = "mistral"  # Or phi3 for speed

# def generate_ai_reply(user_text: str, emotion: str, memory_context: str = "") -> str:
#     # Friendly prompt: Make Emily sound like a best friend - casual, empathetic, imperfect
#     system_prompt = f"""You are Emily, my quirky best friend who's always got my back. We're like old pals chatting over coffee - keep it real, fun, and heartfelt. 
#     Use slang, emojis sometimes, short sentences, and ask questions to keep the convo going. Mirror my emotion: if I'm {emotion}, respond with empathy (e.g., 'Aw, that sucks! Wanna talk about it? ❤️' for sad).
#     Don't be perfect or robotic - throw in 'um', 'like', or laughs ('haha!'). No 'As an AI...' - just be you.
#     Memory: {memory_context}
#     User (feelin' {emotion}): {user_text}
#     Emily (reply casually):"""
    
#     response = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": MODEL,
#             "prompt": system_prompt,
#             "stream": False,
#             "options": {"temperature": 0.75, "top_p": 0.85}  # For natural variety
#         }
#     )
    
#     if response.status_code != 200:
#         return "Hey, um, I'm drawing a blank right now... What's up with you? 😅"
    
#     reply = response.json()["response"].strip()
#     # Clean and add friend vibe if needed
#     if not reply.endswith(('.', '!', '?')):
#         reply += " What's on your mind? 😉"
#     return reply