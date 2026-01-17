import os


def suggest_action(action: dict):
    if action["type"] == "pc":
        print(f"⚠️ Suggested PC action: {action['command']}")
        print("Type CONFIRM to execute or ignore.")
        confirmation = input("Your choice: ")
        if confirmation.strip().upper() == "CONFIRM":
            os.system(action["command"])
            print("✅ Action executed.")