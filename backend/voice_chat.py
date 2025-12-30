# voice_chat.py

from whisper_test import speech_to_text
from emotion_engine import detect_emotion
from response_engine import generate_reply
from voice_emotion_map import get_voice_settings
from voice_clone import speak
from memory import Memory
from emotion_state import update_emotion
from chat import listen_once

import time
import traceback

memory = Memory()

def main():
    print("\n🎤 Emily AI – Voice Chat Started")
    print("Speak naturally (Ctrl+C to stop)\n")

    while True:
        try:
            # 1️⃣ Listen
            print("🎧 Listening...")
            audio = listen_once()

            if audio is None:
                print("⚠️ No audio captured")
                continue

            # 2️⃣ Speech → Text
            text = speech_to_text(audio)

            if not text or not text.strip():
                print("⚠️ No speech detected")
                continue

            print(f"🧑 You: {text}")

            # 3️⃣ Emotion Detection
            emotion, scores = detect_emotion(text)
            emotion_info = update_emotion(emotion)

            print(f"🎭 Emotion: {emotion}")
            print(f"📊 Scores: {scores}")

            # 4️⃣ Voice Settings (FIXED)
            voice_settings = get_voice_settings(emotion)

            # 5️⃣ AI Reply (Ollama / Mistral)
            reply = generate_reply(
                text,
                emotion_info["current"],
                memory.context()
            )

            memory.add(text, reply)

            print(f"🤖 Emily: {reply}")

            # 6️⃣ Speak
            speak(reply, voice_settings)

            print("────────────────────────────")

        except KeyboardInterrupt:
            print("\n🛑 Voice chat stopped by user")
            break

        except Exception as e:
            print("❌ Error:", e)
            traceback.print_exc()
            time.sleep(1)

if __name__ == "__main__":
    main()
