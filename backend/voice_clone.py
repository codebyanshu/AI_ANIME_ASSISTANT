import sounddevice as sd
import soundfile as sf
from TTS.api import TTS

MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
tts = TTS(model_name=MODEL)

VOICE = "voices/my_voice.wav"
OUTPUT_PATH = "output/output.wav"

def speak(text, settings):
    tts.tts_to_file(
        text=text,
        speaker_wav=VOICE,
        language="en",
        file_path=OUTPUT_PATH,
        temperature=settings["temperature"],
        speed=settings["speed"]
    )

    # 🔊 PLAY AUDIO
    data, samplerate = sf.read(OUTPUT_PATH)
    sd.play(data, samplerate)
    sd.wait()
