from transformers import pipeline
from typing import Dict, Tuple

# Load emotion classifier (DistilBERT - accurate for text emotions)
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", return_all_scores=True)

emotion_state = {
    "current": "neutral",
    "intensity": 0.5
}

def detect_emotion(text: str) -> Tuple[str, Dict[str, float]]:
    if not text.strip():
        return "neutral", {"neutral": 1.0}
    
    scores = emotion_classifier(text)[0]["scores"]  # List of dicts: [{'label': 'joy', 'score': 0.8}, ...]
    emotion_scores = {item['label']: item['score'] for item in scores}
    
    # Map to core emotions
    emotion_map = {
        'joy': 'happy', 'sadness': 'sad', 'anger': 'angry',
        'fear': 'fear', 'surprise': 'surprise', 'disgust': 'angry', 'neutral': 'calm'
    }
    mapped_scores = {}
    for label, score in emotion_scores.items():
        core = emotion_map.get(label, 'neutral')
        if core not in mapped_scores:
            mapped_scores[core] = 0
        mapped_scores[core] = max(mapped_scores[core], score)
    
    emotion = max(mapped_scores.items(), key=lambda x: x[1])[0]
    emotion_state["current"] = emotion
    emotion_state["intensity"] = max(mapped_scores.values())
    return emotion, mapped_scores

def update_emotion(new_emotion: str, confidence=0.6) -> Dict[str, float]:
    if new_emotion == emotion_state["current"]:
        emotion_state["intensity"] = min(1.0, emotion_state["intensity"] + 0.1)
    else:
        emotion_state["current"] = new_emotion
        emotion_state["intensity"] = confidence
    return emotion_state