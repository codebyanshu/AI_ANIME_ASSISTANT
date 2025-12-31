import sounddevice as sd
import soundfile as sf
import torch
import numpy as np
from TTS.api import TTS
import random  # For natural fillers

MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
tts = TTS(model_name=MODEL)
VOICE = "voices/my_voice.wav"  # Your cloned voice
OUTPUT_PATH = "output/response.wav"

def add_pauses(text: str, pause_prob: float) -> str:
    """Add natural pauses/fillers for friendly feel."""
    if random.random() < pause_prob:
        fillers = ["um...", "like...", "you know?", "haha"]
        text = random.choice(fillers) + " " + text
    # Add ellipsis for pauses
    if "..." not in text and random.random() < 0.2:
        text = text.replace('.', '... ')
    return text

def speak(text: str, settings: dict):
    # Enhance text with emotion
    enhanced_text = add_pauses(text, settings["pause_prob"])
    
    # XTTS with emotion params (temperature for variance, speed via post-process)
    tts.tts_to_file(
        text=enhanced_text,
        speaker_wav=VOICE,
        language="en",
        file_path=OUTPUT_PATH,
        temperature=settings["temperature"],
        # Speed: XTTS doesn't direct; simulate by resampling audio
    )
    
    # Post-process: Resample for speed/pitch (simple)
    data, sr = sf.read(OUTPUT_PATH)
    speed_factor = settings["speed"]
    new_len = int(len(data) / speed_factor)
    resampled = np.interp(np.linspace(0, len(data)-1, new_len), np.arange(len(data)), data)
    # Pitch: Basic shift (not perfect; use librosa for advanced)
    if settings["pitch_shift"] != 0:
        # Simple: Repeat/shift samples
        shift_samples = int(len(resampled) * settings["pitch_shift"] / 12)  # Rough semitone
        resampled = np.roll(resampled, shift_samples)
    
    sf.write(OUTPUT_PATH, resampled, int(sr / speed_factor))
    
    # Play
    play_data, play_sr = sf.read(OUTPUT_PATH)
    sd.play(play_data, play_sr)
    sd.wait()