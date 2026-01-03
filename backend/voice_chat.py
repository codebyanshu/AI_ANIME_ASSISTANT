# In voice_chat.py or similar
import sys
from .vad_listener import listen_for_speech  # Assuming
from .response_engine import craft_response
from .voice_clone import speak_response  # Assuming TTS

def main_loop():
    print("Emily: Hey bestie! I'm here - just chat away. 💕")
    while True:
        user_input = listen_for_speech()  # Gets transcribed text
        if user_input.lower() == "exit":
            sys.exit()
        
        emotion_state = {}  # From emotion_engine
        response = craft_response(user_input, emotion_state)
        print(f"Emily: {response}")
        speak_response(response)  # TTS

if __name__ == "__main__":
    main_loop()