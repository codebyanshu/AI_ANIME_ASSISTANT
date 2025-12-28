import subprocess
import sys

print("Local AI Chat (type 'exit' to quit)")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    result = subprocess.run(
        ["ollama", "run", "llama3", user_input],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    print("AI:", result.stdout)
