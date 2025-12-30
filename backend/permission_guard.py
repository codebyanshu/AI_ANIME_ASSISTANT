def require_confirmation(intent: str) -> bool:
    dangerous = ["open_browser", "open_notepad", "shutdown"]

    return intent in dangerous
if __name__ == "__main__":
    test_intents = [
        "open_browser",
        "open_notepad",
        "shutdown",
        "chat"
    ]

    for intent in test_intents:
        needs_confirmation = require_confirmation(intent)
        print(f"Intent: {intent} => Requires Confirmation: {needs_confirmation}")
# - --- IGNORE ---
# File: backend/intent_parser.py
# --- a/file:///a%3A/AI_ANIME_ASSISTANT/backend/intent_parser.py
# +++ b/file:///a%3A/AI_ANIME_ASSISTANT/backend/intent_parser