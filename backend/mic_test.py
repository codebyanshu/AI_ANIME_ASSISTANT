import sounddevice as sd
import numpy as np
import wave

duration = 5  # seconds
samplerate = 16000

print("Recording for 5 seconds... Speak now!")

audio = sd.rec(
    int(duration * samplerate),
    samplerate=samplerate,
    channels=1,
    dtype=np.int16
)

sd.wait()

with wave.open("test.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(samplerate)
    wf.writeframes(audio.tobytes())

print("Recording saved as test.wav")
