def get_voice_settings(emotion):
    return {
        "calm": {"temperature": 0.65, "speed": 0.9},
        "happy": {"temperature": 0.9, "speed": 1.05},
        "sad": {"temperature": 0.55, "speed": 0.8},
        "angry": {"temperature": 1.0, "speed": 1.1},
    }.get(emotion, {"temperature": 0.7, "speed": 0.9})
