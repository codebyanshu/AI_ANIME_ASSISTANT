import os
import webbrowser

def execute_action(intent: str):
    if intent == "open_browser":
        webbrowser.open("https://google.com")
        return "Opening browser."
    if intent == "open_notepad":
        os.system("notepad")
        return "Opening Notepad."
    return "Action not allowed."

if __name__ == "__main__":
    test_intents = [
        "open_browser",
        "open_notepad",
        "shutdown"
    ]
    for intent in test_intents:
        result = execute_action(intent)
        print(f"Intent: {intent} => Result: {result}")