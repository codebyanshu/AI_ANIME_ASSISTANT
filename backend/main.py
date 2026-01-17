import asyncio
from llm import ask_llm
from text_processing import prepare_speech
from tts import speak
from pc_control import suggest_action

async def main():
    while True:
        user = input("You: ")

        if user.lower() in ["exit", "quit"]:
            break

        data = ask_llm(user)

        print("📺 DISPLAY:\n", data["display"])

        speech = prepare_speech(data)
        await speak(speech, data["emotion"])

        if data["action"]["type"] != "none":
            suggest_action(data["action"])

asyncio.run(main())
