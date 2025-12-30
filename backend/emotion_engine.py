# emotion_engine.py
from typing import Dict, Tuple

emotion_state = {
    "current": "calm",
    "intensity": 0.5
}

def detect_emotion(text: str) -> Tuple[str, Dict[str, float]]:
    text = text.lower()

    scores = {
        "sad": 0.0,
        "happy": 0.0,
        "angry": 0.0,
        "calm": 0.2
    }

    if any(w in text for w in ["sad", "tired", "alone", "cry"]):
        scores["sad"] += 0.6
    if any(w in text for w in ["happy", "great", "love", "excited"]):
        scores["happy"] += 0.6
    if any(w in text for w in ["angry", "hate", "annoyed"]):
        scores["angry"] += 0.6

    emotion = max(scores, key=scores.get)
    emotion_state["current"] = emotion
    emotion_state["intensity"] = scores[emotion]

    return emotion, scores

