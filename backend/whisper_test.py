import numpy as np
import wave
import tempfile
import os

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

_whisper_model = None

def _get_whisper():
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    if WhisperModel is None:
        raise RuntimeError("faster-whisper not installed; install with 'pip install faster-whisper'")
    _whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
    return _whisper_model


def speech_to_text(audio, sample_rate=16000):
    model = _get_whisper()
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


def _write_wav_file(audio: np.ndarray, sample_rate: int, filename: str):
    """Write a mono numpy array to a 16-bit PCM WAV file."""
    if audio.ndim > 1:
        audio = audio[:, 0]

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
    test_path = "test.wav"
    if os.path.exists(test_path):
        try:
            model = _get_whisper()
            segments, info = model.transcribe(test_path, language="en")
            print("Detected language:", info.language)
            for segment in segments:
                print(segment.text)
        except Exception as e:
            print("Whisper model error:", e)
    else:
        print("No test.wav found; module loaded successfully.")