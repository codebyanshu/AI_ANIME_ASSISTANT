import subprocess
import sys
import sounddevice as sd
import numpy as np
    # if emotion == "sad":
    #     return "That sounds really heavy… I'm here with you."
    # if emotion == "happy":
    #     return "That makes me smile. Tell me more."
    # if emotion == "angry":
    #     return "I can feel that frustration. Want to talk about it?"
    # if emotion == "calm":
    #     return "I am happy to see you at peace."
    
    # return "I'm listening."

def generate_reply(text):
        # try:
    user_input = text

    result = subprocess.run(
        ["ollama", "run", "llama3", user_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

    return result.stdout