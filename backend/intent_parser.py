def detect_intent(text: str):
    text = text.lower()
    if "open" in text and "browser" in text:
        return "open_browser"
    if "open" in text and "notepad" in text:
        return "open_notepad"
    if "shutdown" in text or "restart" in text:
        return "dangerous"
    return "chat"

def handle_action(text: str):
    intent = detect_intent(text)
    if intent == "open_browser":
        return "open chrome"
    elif intent == "open_notepad":
        return "open notepad"
    elif intent == "dangerous":
        return "Action denied for safety reasons."
    else:
        return None

if __name__ == "__main__":
    test_texts = [
        "Can you open the browser for me?",
        "Please open notepad.",
        "I want to shutdown my computer.",
        "Let's chat about something."
    ]
    for text in test_texts:
        action = handle_action(text)
        print(f"Input: {text} => Action: {action}")