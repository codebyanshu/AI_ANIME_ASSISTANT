import time
import traceback

from whisper_test import speech_to_text
from emotion_engine import detect_emotion
from response_engine import generate_reply
from voice_emotion_map import get_voice_settings
from voice_clone import speak
from memory import Memory
from chat import listen_once

# SAFE ACTION CONTROL
from action_controller import can_execute, execute_command

memory = Memory()


def main():
    print("\n🎤 Emily AI - Voice Chat Started (Step 20)\n")

    while True:
        try:
            # 🎧 Listen
            print("🎧 Listening...")
            audio = listen_once()

            if audio is None:
                continue

            # 🗣 Speech → Text
            text = speech_to_text(audio)
            if not text or not text.strip():
                print("⚠️ No speech detected")
                continue

            print(f"🧑 You: {text}")

            # 🎭 Emotion detection
            emotion, scores = detect_emotion(text)
            print(f"🎭 Emotion: {emotion}")
            
            

            # 🎛 Voice settings
            voice_settings = get_voice_settings(emotion)

            # ================= STEP 20: SAFE ACTION CONTROL =================
            text_lower = text.lower()

            if any(word in text_lower for word in ["open", "start", "launch"]):

                if can_execute(text_lower):
                    print(f"🛑 Permission required to run: '{text_lower}'")
                    confirm = input("Type YES to confirm: ").strip().lower()

                    if confirm == "yes":
                        success, msg = execute_command(text_lower)
                        reply = msg
                    else:
                        reply = "Action cancelled."

                    memory.add(text, reply)
                    print(f"🤖 Emily: {reply}")
                    speak(reply, voice_settings)
                    print("────────────────────────")
                    continue  # VERY IMPORTANT

            # ================= NORMAL CHAT =================
            reply = generate_reply(text, emotion, memory.context())
            memory.add(text, reply)

            print(f"🤖 Emily: {reply}")
            speak(reply, voice_settings)
            print("────────────────────────")

        except KeyboardInterrupt:
            print("\n🛑 Voice chat stopped.")
            break

        except Exception as e:
            print("❌ Error:", e)
            traceback.print_exc()
            time.sleep(1)


if __name__ == "__main__":
    main()
