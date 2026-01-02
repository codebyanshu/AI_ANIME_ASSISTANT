try:
    import sounddevice as sd
except Exception:
    sd = None
import numpy as np
import wave

duration = 5  # seconds
samplerate = 16000

def record_test(filename="test.wav"):
    if sd is None:
        raise RuntimeError("sounddevice not available; install with 'pip install sounddevice'")
    print("Recording for 5 seconds... Speak now!")
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype=np.int16
    )
    sd.wait()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
    print(f"Recording saved as {filename}")

if __name__ == "__main__":
    record_test()
