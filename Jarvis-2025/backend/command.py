import asyncio
import edge_tts
import os
import time
import speech_recognition as sr
import eel
from playsound import playsound
from threading import Thread

# =========================
# EDGE TTS CONFIG
# =========================
VOICE = "en-US-JennyNeural"   # calm female voice
RATE = "+0%"
VOLUME = "+0%"
OUTPUT_FILE = "voice.mp3"

# =========================
# EDGE TTS SPEAK FUNCTION
# =========================
async def _edge_speak_async(text: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=RATE,
        volume=VOLUME
    )
    await communicate.save(OUTPUT_FILE)

    playsound(OUTPUT_FILE)
    os.remove(OUTPUT_FILE)

def speak(text):
    text = str(text)

    try:
        eel.DisplayMessage(text)
    except:
        pass

    Thread(
        target=lambda: asyncio.run(_edge_speak_async(text)),
        daemon=True
    ).start()

    try:
        eel.receiverText(text)
    except:
        pass


# =========================
# SPEECH TO TEXT
# =========================
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")

        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=0.5)

        audio = r.listen(source, timeout=10, phrase_time_limit=8)

    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")

        query = r.recognize_google(audio, language="en-US")
        print(f"User said: {query}")
        eel.DisplayMessage(query)

        return query.lower()

    except Exception as e:
        print("Speech recognition error:", e)
        speak("Sorry, I didn't catch that.")
        return None


# =========================
# MAIN COMMAND HANDLER
# =========================
@eel.expose
def takeAllCommands(message=None):

    if message is None:
        query = takecommand()
        if not query:
            return
        eel.senderText(query)
    else:
        query = message.lower()
        print(f"Message received: {query}")
        eel.senderText(query)

    try:
        if "open" in query:
            from backend.feature import openCommand
            openCommand(query)

        elif "send message" in query or "call" in query or "video call" in query:
            from backend.feature import findContact, whatsApp

            phone, name = findContact(query)
            if phone == 0:
                speak("I couldn't find that contact.")
                return

            if "send message" in query:
                speak("What message should I send?")
                msg = takecommand()
                if msg:
                    whatsApp(phone, msg, "message", name)

            elif "video call" in query:
                whatsApp(phone, query, "video call", name)

            else:
                whatsApp(phone, query, "call", name)

        elif "on youtube" in query:
            from backend.feature import PlayYoutube
            PlayYoutube(query)

        else:
            from backend.feature import chatBot
            chatBot(query)

    except Exception as e:
        print("Command error:", e)
        speak("Sorry, something went wrong.")

    eel.ShowHood()
