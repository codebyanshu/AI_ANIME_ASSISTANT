import time
import traceback
from vad_listener import VADListener  # New VAD
from emotion_engine import detect_emotion, update_emotion  # Fixed
from response_engine import generate_reply  # Uses fixed LLM
from voice_emotion_map import get_voice_settings  # Fixed
from voice_clone import speak  # Fixed
from memory import Memory
from action_controller import ActionController  # Your updated one

memory = Memory()
controller = ActionController()

def main():
    print("\nEmily: Hey bestie! I'm here - just chat away. I'll listen till you're done. 💕\n")
    
    listener = VADListener()
    
    def on_utterance(text):
        if not text.strip():
            return
        
        print(f"You: {text}")
        
        # Emotion detection (fixed)
        emotion, scores = detect_emotion(text)
        update_emotion(emotion, scores.get(emotion, 0.5))
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
        while True:
            listener.listen(on_utterance)
            time.sleep(0.5)  # Brief pause between utterances
    except KeyboardInterrupt:
        print("\nEmily: Aww, catch you later! Bye! 👋")
    except Exception as e:
        print("Oops:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()