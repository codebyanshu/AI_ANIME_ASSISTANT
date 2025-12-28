import sounddevice as sd
import numpy as np
import soundfile as sf
import whisper
from TTS.api import TTS
import time

# ================= SETTINGS =================
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
SPEAKER_WAV = "voices/my_voice.wav"
OUTPUT_PATH = "output/output.wav"
LANGUAGE = "en"

SAMPLE_RATE = 16000
RECORD_SECONDS = 6
WAKE_WORD = "hello"
# ==========================================

print("🔁 Loading models...")
whisper_model = whisper.load_model("base")
tts = TTS(model_name=MODEL_NAME)

# -------- Emotion Detection --------
def detect_emotion(text):
    text = text.lower()
    if any(w in text for w in ["sad", "tired", "lonely", "cry"]):
        return "sad"
    if any(w in text for w in ["happy", "great", "love", "awesome"]):
        return "happy"
    if any(w in text for w in ["angry", "mad", "hate"]):
        return "angry"
    return "calm"

# -------- Reply Generator --------
def generate_reply(text):
    return f"I heard you say {text}. I'm here with you."

print("\n🎧 Emily is now listening...")
print("Say: 'Hey Emily' to activate\n")

try:
    while True:
        # Listen continuously
        audio = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE),
                        samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype="float32")
        sd.wait()

        sf.write("temp.wav", audio, SAMPLE_RATE)

        result = whisper_model.transcribe("temp.wav")
        text = str(result["text"]).lower().strip()

        if not text:
            continue

        print("🧑 You said:", text)

        # Wake word check
        if WAKE_WORD not in text:
            print("🟡 Waiting for wake word...")
            continue

        print("✅ Wake word detected")

        emotion = detect_emotion(text)
        print(f"🎭 Emotion: {emotion}")

        reply = generate_reply(text)

        tts.tts_to_file(
            text=reply,
            speaker_wav=SPEAKER_WAV,
            language=LANGUAGE,
            file_path=OUTPUT_PATH,
            temperature=0.9,
            speed=1.0
        )

        print("🔊 Emily spoke\n")

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
