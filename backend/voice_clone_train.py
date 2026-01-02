# -------------------------------
# Voice Cloning using Coqui TTS
# -------------------------------
import os
import soundfile as sf
import numpy as np

# Create output folder (unchanged)
os.makedirs("output", exist_ok=True)

# ========== SETTINGS ==========
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

LANGUAGE = "en"
SPEAKER_WAV = r"A:\AI_ANIME_ASSISTANT\voices\my_voice.wav"
OUTPUT_PATH = "output/output_n.wav"

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
    
    "I'm so full of joy today!, Everything feels so bright and wonderful!, I just want to share this happiness with everyone!",
]

def main():
    print("Loading model...")
    try:
        from TTS.api import TTS
    except Exception:
        print("TTS package not available. Install requirements with: pip install -r requirements.txt")
        raise

    tts = TTS(model_name=MODEL_NAME)

    audio_chunks = []
    sample_rate = 22050

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

        # tts.tts may return a numpy array or a tuple (array, sr)
        if isinstance(wav, tuple) and len(wav) >= 1:
            audio = wav[0]
            if len(wav) > 1 and isinstance(wav[1], int):
                sample_rate = wav[1]
        else:
            audio = wav

        audio = np.asarray(audio, dtype=np.float32)
        audio_chunks.append(audio)

    # -------------------------------
    # Merge all lines into one output
    # -------------------------------
    # create short silence between lines (0.2s)
    silence = np.zeros(int(0.2 * sample_rate), dtype=np.float32)

    if audio_chunks:
        final_audio = [item for pair in ((chunk, silence) for chunk in audio_chunks) for item in pair]
        final_audio = np.concatenate(final_audio)
    else:
        final_audio = np.array([], dtype=np.float32)

    sf.write(OUTPUT_PATH, final_audio, sample_rate)

    print("Emotional voice generated successfully!")
    print(f"Saved at: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
