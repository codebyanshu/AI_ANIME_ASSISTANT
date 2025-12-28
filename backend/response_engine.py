def generate_reply(text, emotion, memory_context):
    if emotion == "sad":
        return "I'm here with you. You can talk freely, I'm listening."
    if emotion == "happy":
        return "I love hearing you this excited. What happened next?"
    if emotion == "angry":
        return "It sounds intense. Want to tell me what made you feel this way?"

    # calm / neutral
    if len(text.split()) < 4:
        return "Can you tell me a little more?"

    return "That's interesting. Tell me more about it."



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