def get_voice_settings(emotion):
    # Enhanced: Add pitch/speed/pauses for natural emotion
    base_settings = {
        "temperature": 0.7,  # Creativity
        "speed": 1.0,
        "pitch_shift": 0,    # XTTS extension: Simulate via post-process or model
        "pause_prob": 0.1    # Add filler pauses
    }
    
    emotion_map = {
        "happy": {"temperature": 0.95, "speed": 1.1, "pitch_shift": 0.2, "pause_prob": 0.05},
        "sad": {"temperature": 0.6, "speed": 0.85, "pitch_shift": -0.3, "pause_prob": 0.3},
        "angry": {"temperature": 1.0, "speed": 1.15, "pitch_shift": 0.1, "pause_prob": 0.1},
        "fear": {"temperature": 0.65, "speed": 1.2, "pitch_shift": 0.4, "pause_prob": 0.2},
        "surprise": {"temperature": 0.9, "speed": 1.3, "pitch_shift": 0.3, "pause_prob": 0.05},
        "calm": {"temperature": 0.65, "speed": 0.95, "pitch_shift": 0, "pause_prob": 0.15},
        "neutral": base_settings
    }
    return emotion_map.get(emotion, base_settings)