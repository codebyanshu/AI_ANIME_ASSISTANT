# -------------------------------
# Voice Cloning using Coqui TTS
# -------------------------------
import os
from TTS.api import TTS
import soundfile as sf

# Create output folder (unchanged)
os.makedirs("output", exist_ok=True)

# ========== SETTINGS ==========
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

LANGUAGE = "en"
SPEAKER_WAV =r"A:\AI_ANIME_ASSISTANT\backend\voice\part_1.wav"
OUTPUT_PATH ="output/output_fin.wav"

# ==============================

# -------------------------------
# EMOTION BOOSTER TEXT (split)
# -------------------------------
TEXT_LINES = [
    "Heyyy I'm really happy youre here… . You know, talking to you always makes me smile. Hehe… I hope you're having a nice day.",

     " H-hello there!, I-I'm so happy to see you!, E-even though I'm a bit shy, I really want to be friends with you!~",

     " Oh... I feel a bit down today., Sometimes things just don't go my way., But talking to you makes me feel better.",

     "Ugh! This is so frustrating!, I can't believe this is happening!, Why does everything have to be so difficult?!",
     
    "Everything is peaceful and quiet., I feel so relaxed right now., Just enjoying the moment. Umm… h-hi… . I was a little nervous to talk, but… . I'm really glad you're here.",

     "Oh wow!! This is amazing!, I can't believe this is happening!, Let's gooo!!",
    
    "I'm so full of joy today!, Everything feels so bright and wonderful!, I just want to share this happiness with everyone!",]

def main():
    print("Loading model...")
    tts = TTS(model_name=MODEL_NAME)

    audio_chunks = []

    print("Generating emotional voice (line by line)...")

    for line in TEXT_LINES:
        wav = tts.tts(
            text=line,
            speaker_wav=SPEAKER_WAV,
            language=LANGUAGE,
            temperature=0.75,
            top_p=0.85,
            speed=0.85
        )

        audio_chunks.append(wav)

    # -------------------------------
    # Merge all lines into one output
    # -------------------------------
    final_audio = []
    silence = [0.0] * int(0.2 * 22050)  # 0.2 sec pause

    for chunk in audio_chunks:
        final_audio.extend(chunk)
        final_audio.extend(silence)

    sf.write(OUTPUT_PATH, final_audio, 22050)

    print("✅ Emotional voice generated successfully!")
    print(f"Saved at: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
