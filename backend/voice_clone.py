from TTS.api import TTS

MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
tts = TTS(model_name=MODEL)
VOICE = "voices/my_voice.wav"

def speak(text, settings):
    tts.tts_to_file(
        text=text,
        speaker_wav=VOICE,
        language="en",
        file_path="output/output.wav",
        temperature=settings["temperature"],
        speed=settings["speed"]
    )
