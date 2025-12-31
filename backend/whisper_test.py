from faster_whisper import WhisperModel
import numpy as np
import wave
import tempfile
import os

model = WhisperModel("small", device="cpu", compute_type="int8")

def speech_to_text(audio, sample_rate=16000):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.close()

    audio_int16 = (audio * 32767).astype("int16")
    with wave.open(tmp.name, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    segments, _ = model.transcribe(tmp.name)
    os.remove(tmp.name)

    return "".join(seg.text for seg in segments).strip()

# Initialize model once at import (heavy but acceptable). Do NOT transcribe here.

def _write_wav_file(audio: np.ndarray, sample_rate: int, filename: str):
    """Write a mono numpy array to a 16-bit PCM WAV file."""
    if audio.ndim > 1:
        # Take first channel if multi-channel
        audio = audio[:, 0]

    # Ensure float -> int16
    if np.issubdtype(audio.dtype, np.floating):
        audio_int16 = (audio * 32767).astype(np.int16)
    else:
        audio_int16 = audio.astype(np.int16)

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

if __name__ == "__main__":
    # Simple manual test when executed directly (won't run on import)
    test_path = "test.wav"
    if os.path.exists(test_path):
        segments, info = model.transcribe(test_path, language="en")
        print("Detected language:", info.language)
        for segment in segments:
            print(segment.text)
    else:
        print("No test.wav found; module loaded successfully.")