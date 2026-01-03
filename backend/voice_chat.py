import time
import traceback
from vad_listener import VADListener  # Fixed: Absolute import (no . prefix for direct run)
from emotion_engine import detect_emotion, update_emotion
from response_engine import generate_reply
from voice_emotion_map import get_voice_settings
from voice_clone import speak
from memory import Memory
from action_controller import ActionController

memory = Memory()
controller = ActionController()

def main():
    print("\nEmily: Hey bestie! I'm here - just chat away. I'll listen till you're done. 💕\n")
    print("Emily's listening... (speak now!)")  # MOVED: Print only once here
    
    listener = VADListener()
    
    def on_utterance(text):
        if text is None:  # NEW: Handle no-speech timeout
            print("Speech not detected.")  # Only print this once per attempt
            return
        
        if not text.strip():
            return
        
        print(f"You: {text}")
        
        # Emotion detection (fixed)
        emotion, scores = detect_emotion(text)
        update_emotion(emotion, scores.get(emotion, 0.5))  # FIXED: Matches 2-arg def
        print(f"Emily senses: {emotion} 😊")
        
        # Action check (your controller)
        cmd_dict = controller.normalize_command(text)
        if cmd_dict["intent"] != "unknown" and controller.can_execute(cmd_dict):
            success, msg = controller.execute_command(cmd_dict)
            reply = f"{msg} Anything else, pal?"
            # Speak action reply
            voice_settings = get_voice_settings(emotion)
            speak(reply, voice_settings)
            memory.add(text, reply)
            print(f"Emily: {reply}")
            print("────────────────────────")
            return
        
        # Normal chat (friendly LLM)
        reply = generate_reply(text, emotion, memory.context())
        memory.add(text, reply)
        
        print(f"Emily: {reply}")
        voice_settings = get_voice_settings(emotion)
        speak(reply, voice_settings)
        print("────────────────────────")
    
    try:
        listener.listen(on_utterance)  # REMOVED while True loop: Now continuous inside listen()
    except KeyboardInterrupt:
        print("\nEmily: Aww, catch you later! Bye! 👋")
    except Exception as e:
        print("Oops:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()