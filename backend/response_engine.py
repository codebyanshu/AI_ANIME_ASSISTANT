from typing import Dict
from .llm_engine import generate_response
from .emotion_engine import detect_emotion  # Assuming this exists for emotion
from .memory import get_conversation_history  # Assuming memory module for context

def craft_response(user_text: str, emotion_state: Dict[str, float]) -> str:
    """
    Craft Emily's response based on user input, emotion, and history.
    """
    # Detect emotion (from your existing code)
    emotion, _ = detect_emotion(user_text)
    
    # Get history for context (adjust if your memory is different)
    history = get_conversation_history()  # Placeholder; implement as needed
    
    # Build prompt with emotion and personality
    prompt = f"User said: {user_text}. They seem {emotion}. Respond as Emily."
    if history:
        prompt = f"Previous chat: {history}\n" + prompt
    
    # Generate using API
    response = generate_response(prompt, max_tokens=100, temperature=0.8 if emotion == "happy" else 0.6)
    
    # Add emoji based on emotion (customize)
    if emotion == "happy":
        response += " 😍"
    elif emotion == "sad":
        response += " 🥺"
    
    return response