emotion_state = {
    "current": "calm",
    "intensity": 0.5
}

def update_emotion(new_emotion, confidence=0.6):
    if new_emotion == emotion_state["current"]:
        emotion_state["intensity"] = min(1.0, emotion_state["intensity"] + 0.1)
    else:
        emotion_state["current"] = new_emotion
        emotion_state["intensity"] = confidence

    return emotion_state
