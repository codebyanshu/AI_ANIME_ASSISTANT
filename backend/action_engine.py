# action_engine.py
import subprocess
import platform

def handle_action(text: str):
    text = text.lower()

    if "open chrome" in text:
        return open_app("chrome")

    if "open notepad" in text:
        return open_app("notepad")

    return None  # not an action


def open_app(app_name: str):
    try:
        system = platform.system()

        if system == "Windows":
            subprocess.Popen(app_name)
        elif system == "Linux":
            subprocess.Popen([app_name])
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", app_name])

        return f"Opening {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}"
