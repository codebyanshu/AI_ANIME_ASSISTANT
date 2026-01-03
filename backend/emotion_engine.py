from typing import Dict, Tuple

# Try to load transformers pipeline; if unavailable, provide a simple fallback.
try:
    from transformers import pipeline
    emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", return_all_scores=True)
except Exception:
    emotion_classifier = None

emotion_state = {
    "current": "neutral",
    "intensity": 0.5
}


def _fallback_detect(text: str):
    words = text.lower()
    if any(w in words for w in ("happy", "joy", "glad", "love", "amazing")):
        return "happy", {"happy": 1.0}
    if any(w in words for w in ("sad", "down", "unhappy", "depressed")):
        return "sad", {"sad": 1.0}
    if any(w in words for w in ("angry", "mad", "furious", "hate")):
        return "angry", {"angry": 1.0}
    return "calm", {"calm": 1.0}


def detect_emotion(text: str) -> Tuple[str, Dict[str, float]]:
    if not text.strip():
        return "neutral", {"neutral": 1.0}
    if emotion_classifier is None:
        emotion, scores = _fallback_detect(text)
        emotion_state["current"] = emotion
        emotion_state["intensity"] = max(scores.values())
        return emotion, scores

    try:
        scores = emotion_classifier(text)[0]["scores"]
        emotion_scores = {item["label"]: item["score"] for item in scores}
        emotion_map = {
            "joy": "happy", "sadness": "sad", "anger": "angry",
            "fear": "fear", "surprise": "surprise", "disgust": "angry", "neutral": "calm"
        }
        mapped_scores = {}
        for label, score in emotion_scores.items():
            core = emotion_map.get(label, "neutral")
            mapped_scores[core] = max(mapped_scores.get(core, 0), score)

        emotion = max(mapped_scores.items(), key=lambda x: x[1])[0]
        emotion_state["current"] = emotion
        emotion_state["intensity"] = max(mapped_scores.values())
        return emotion, mapped_scores
    except Exception:
        return _fallback_detect(text)


def update_emotion(new_emotion: str, confidence: float = 0.6) -> Dict[str, float]:  # FIXED: Explicit 2-arg signature (confidence optional)
    """Update current emotion state with new emotion and confidence/intensity."""
    if new_emotion == emotion_state["current"]:
        emotion_state["intensity"] = min(1.0, emotion_state["intensity"] + 0.1 * confidence)  # Use confidence to scale
    else:
        emotion_state["current"] = new_emotion
        emotion_state["intensity"] = confidence
    return emotion_state