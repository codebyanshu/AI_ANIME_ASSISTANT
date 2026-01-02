try:
    from .llm_engine import generate_ai_reply
except Exception:
    # fallback to import-by-name for direct execution (non-package)
    try:
        from llm_engine import generate_ai_reply
    except Exception:
        generate_ai_reply = None


def generate_reply(user_text, emotion, memory_context=""):
    if callable(generate_ai_reply):
        return generate_ai_reply(user_text, emotion, memory_context)
    return "Sorry, the LLM engine is not available."


# import requests

# OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL_NAME = "mistral"   # or llama3, phi, etc

# def generate_reply(user_text, emotion, memory_context):
#     prompt = f"""
# You are Emily, a friendly emotional AI assistant.

# Emotion: {emotion}
# Memory:
# {memory_context}

# User said:
# {user_text}

# Reply naturally, emotionally, and helpfully.
# """

#     response = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": MODEL_NAME,
#             "prompt": prompt,
#             "stream": False
#         }
#     )

#     if response.status_code != 200:
#         return "Sorry, my thinking engine is not responding."

#     return response.json()["response"].strip()



# def generate_reply(text, emotion, memory_context):
#     if emotion == "sad":
#         return "I'm here with you. You can talk freely, I'm listening."
#     if emotion == "happy":
#         return "I love hearing you this excited. What happened next?"
#     if emotion == "angry":
#         return "It sounds intense. Want to tell me what made you feel this way?"

#     # calm / neutral
#     if len(text.split()) < 4:
#         return "Can you tell me a little more?"

#     return "That's interesting. Tell me more about it."



# import subprocess
# import sys
# import sounddevice as sd
# import numpy as np
    # if emotion == "sad":
    #     return "That sounds really heavy… I'm here with you."
    # if emotion == "happy":
    #     return "That makes me smile. Tell me more."
    # if emotion == "angry":
    #     return "I can feel that frustration. Want to talk about it?"
    # if emotion == "calm":
    #     return "I am happy to see you at peace."
    
    # return "I'm listening."

# def generate_reply(text):
#         # try:
#     user_input = text

#     result = subprocess.run(
#         ["ollama", "run", "llama3", user_input],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             encoding="utf-8",
#             errors="ignore"
#         )

#     return result.stdout