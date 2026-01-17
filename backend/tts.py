import edge_tts, uuid, os
from playsound import playsound
from emotions import EMOTION_VOICE_MAP

VOICE = "en-IE-EmilyNeural"

async def speak(text: str, emotion: str):
    settings = EMOTION_VOICE_MAP.get(emotion, EMOTION_VOICE_MAP["calm"])
    filename = f"voice_{uuid.uuid4().hex}.mp3"

    tts = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=settings["rate"],
        pitch=settings["pitch"]
    )

    await tts.save(filename)
    playsound(filename)
    os.remove(filename)
