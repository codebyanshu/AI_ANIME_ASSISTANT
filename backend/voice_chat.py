# voice_chat.py - Fixed and Updated Main Loop for Your AI Anime Assistant

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file (create one in project root)
load_dotenv()

# Import your modules (adjust names if different in your repo)
from vad_listener import VADListener  # Your VAD class with integrated AssemblyAI STT
from response_engine import craft_response  # Your LLM/response logic
from voice_clone import speak  # The speak function with Camb.AI TTS integration
# If you have emotion detection, import it here
# from emotion_engine import detect_emotion

def main_loop():
    print("Emily: Hey bestie! I'm here - just chat away. 💕")
    
    # Initialize VAD listener (adjust params like sample_rate if needed)
    listener = VADListener()
    
    while True:
        try:
            print("\nListening... Speak now! 🎤")
            user_input = listener.listen_and_transcribe()  # This uses AssemblyAI STT inside vad_listener
            
            if not user_input:
                print("No speech detected or transcription error. Try again!")
                continue
                
            print(f"You: {user_input}")
            
            if user_input.lower().strip() in ["exit", "bye", "quit", "goodbye"]:
                print("Emily: Bye bestie! Talk soon~ 💕")
                speak("Bye bestie! Talk soon!", {"emotion": "happy"})
                sys.exit(0)
            
            # Optional: Detect emotion from user_input or audio (if implemented)
            emotion_state = {"emotion": "neutral"}  # Replace with real detection if available
            
            # Generate response using your LLM (Ollama or whatever)
            response = craft_response(user_input, emotion_state)
            
            print(f"Emily: {response}")
            
            # Speak the response with Camb.AI TTS + post-processing
            settings = {
                "emotion": emotion_state.get("emotion", "neutral"),
                "pause_prob": 0.15,     # Natural pauses for anime-style speech
                "speed": 1.05,         # Slightly faster for energetic feel
                "pitch_shift": 2,      # Higher pitch for cute/anime voice
                "gender": "female",    # Default anime girl
                "output_path": "output/response.wav"
            }
            speak(response, settings)
            
        except KeyboardInterrupt:
            print("\nEmily: See ya! 💕")
            break
        except Exception as e:
            print(f"Error in loop: {e}")
            continue

if __name__ == "__main__":
    main_loop()