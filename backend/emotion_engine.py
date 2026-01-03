from typing import Dict, Tuple

# Try to load transformers pipeline; if unavailable, provide a simple fallback.
try:
    from transformers import pipeline
    # Fixed: Use top_k=None instead of deprecated return_all_scores=True
    emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=None)
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
        # New format with top_k=None: returns list of lists (one list per input)
        # Each inner list is [{'label': 'joy', 'score': 0.95}, ...] sorted by score descending
        prediction = emotion_classifier(text)
        score_list = prediction[0]  # since single input
        emotion_scores = {item["label"]: item["score"] for item in score_list} 

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
        emotion, scores = _fallback_detect(text)
        emotion_state["current"] = emotion
        emotion_state["intensity"] = max(scores.values())
        return emotion, scores


def update_emotion(new_emotion: str, confidence=0.6) -> Dict[str, float]:
    if new_emotion == emotion_state["current"]:
        emotion_state["intensity"] = min(1.0, emotion_state["intensity"] + 0.1)
    else:
        emotion_state["current"] = new_emotion
        emotion_state["intensity"] = confidence
    return emotion_state