import os
import requests
import time
import soundfile as sf
import sounddevice as sd
import numpy as np
import json

from dotenv import load_dotenv
load_dotenv()  # Loads .env automatically

CAMB_API_KEY = os.getenv("CAMB_AI_API_KEY")
CAMB_VOICE_ID = int(os.getenv("CAMB_VOICE_ID", "0"))  # 0 for default if no clone
BASE_URL = "https://client.camb.ai/apis"

import random
import re

def add_pauses(text: str, pause_prob: float = 0.1):
    """
    Adds natural pauses (', ' or '... ') to text for more expressive TTS.
    """
    if not text:
        return text
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    enhanced_sentences = []
    
    for i, sent in enumerate(sentences):
        enhanced_sentences.append(sent.strip())
        
        # Add pause after sentence with probability
        if random.random() < pause_prob and i < len(sentences) - 1:
            if random.random() < 0.5:
                enhanced_sentences.append(", ")  # Short pause
            else:
                enhanced_sentences.append("... ")  # Longer pause
    
    enhanced_text = " ".join(enhanced_sentences)
    return enhanced_text


# ... (imports as before)

def speak(text: str, settings: dict):
    enhanced_text = add_pauses(text, settings.get("pause_prob", 0.1))
    
    # If no cloned voice, Camb.AI falls back to good default based on gender/age
    voice_id = CAMB_VOICE_ID if CAMB_VOICE_ID > 0 else None
    
    emotion = settings.get("emotion", "neutral")
    gender_map = {"female": 2, "male": 1}
    age_map = {"happy": 20, "excited": 18, "child": 12, "sad": 40, "calm": 35, "neutral": 25, "angry": 30}
    gender = gender_map.get(settings.get("gender", "female"), 2)
    age = age_map.get(emotion, 25)
    
    payload = {
        "text": enhanced_text,
        "language": 1,  # English
        "gender": gender,
        "age": age
    }
    if voice_id:
        payload["voice_id"] = voice_id
    
# ... (rest of the try/except with POST /tts, poll, download as before)
# def speak(text: str, settings: dict):
#     enhanced_text = add_pauses(text, settings.get("pause_prob", 0.1))
    
#     # Map emotion to age/gender for style control
#     emotion = settings.get("emotion", "neutral")
#     gender_map = {"female": 2, "male": 1}  # 1=MALE, 2=FEMALE
#     age_map = {
#         "happy": 20, "excited": 18, "child": 12,
#         "sad": 40, "calm": 35, "neutral": 25, "angry": 30
#     }
#     gender = gender_map.get(settings.get("gender", "female"), 2)  # Default anime-style female
#     age = age_map.get(emotion, 25)
    
#     payload = {
#         "text": enhanced_text,
#         "voice_id": CAMB_VOICE_ID,
#         "language": 1,  # 1 = English; check docs for others
#         "gender": gender,
#         "age": age
#         # Optional: "project_name": "MyAssistant", "folder_id": 1
#     }
    
#     headers = {
#         "x-api-key": CAMB_API_KEY,
#         "Content-Type": "application/json"
#     }
    
#     try:
#         # Step 1: Submit TTS task
#         response = requests.post(f"{BASE_URL}/tts", json=payload, headers=headers)
#         response.raise_for_status()
#         task_data = response.json()
#         task_id = task_data["task_id"]
#         print(f"Camb.AI TTS task submitted: {task_id}")
        
#         # Step 2: Poll for completion
#         while True:
#             status_resp = requests.get(f"{BASE_URL}/tts/{task_id}", headers=headers)
#             status_resp.raise_for_status()
#             status_data = status_resp.json()
#             status = status_data.get("status", "").lower()
#             if status == "completed" or status == "success":
#                 run_id = status_data["run_id"]
#                 break
#             elif status == "failed":
#                 raise Exception(f"TTS task failed: {status_data.get('error')}")
#             time.sleep(2)  # Poll every 2 seconds
        
#         # Step 3: Download audio
#         audio_url = f"{BASE_URL}/tts-result/{run_id}"
#         audio_resp = requests.get(audio_url, headers=headers)
#         audio_resp.raise_for_status()
        
#         output_path = settings.get("output_path", "output/response.wav")
#         with open(output_path, "wb") as f:
#             f.write(audio_resp.content)
        
#         # Post-processing: speed and pitch shift
#         data, sr = sf.read(output_path)
#         speed_factor = settings.get("speed", 1.0)
#         if speed_factor != 1.0:
#             new_len = int(len(data) / speed_factor)
#             data = np.interp(np.linspace(0, len(data) - 1, new_len), np.arange(len(data)), data)
        
#         pitch_shift = settings.get("pitch_shift", 0)
#         if pitch_shift != 0:
#             shift_samples = int(len(data) * pitch_shift / 12)
#             data = np.roll(data, shift_samples)
        
#         sf.write(output_path, data, int(sr * speed_factor))  # Adjust rate for speed
        
#         # Play audio
#         play_data, play_sr = sf.read(output_path)
#         sd.play(play_data, play_sr)
#         sd.wait()
        
#     except Exception as e:
#         print(f"Camb.AI TTS error: {e}")
#         # Optional: Add fallback to local TTS here
        
        
        