import subprocess
import sys
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000

def listen_once(duration_seconds: int = 5):
    audio = sd.rec(
        int(duration_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1
    )
    sd.wait()
    return audio.flatten()


def run_local_chat():
    print("Local AI Chat (type 'exit' to quit)")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

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


if __name__ == "__main__":
    run_local_chat()
