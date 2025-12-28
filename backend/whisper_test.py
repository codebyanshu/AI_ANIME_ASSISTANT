from faster_whisper import WhisperModel
import numpy as np
import wave
import tempfile
import os

# Initialize model once at import (heavy but acceptable). Do NOT transcribe here.
model = WhisperModel("small", device="cpu", compute_type="int8")


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


def speech_to_text(audio, sample_rate: int = 16000, language: str = "en") -> str:
    """Transcribe audio.

    - If `audio` is a str, treat it as a filename and transcribe it.
    - If `audio` is a numpy array (1-D or 2-D), write a temporary WAV and transcribe.
    Returns the concatenated transcript as a single string.
    """
    if isinstance(audio, str):
        segments, info = model.transcribe(audio, language=language)
        return "".join(segment.text for segment in segments)

    # Assume numpy array
    try:
        import numpy as _np
    except Exception:
        raise RuntimeError("speech_to_text expects a filename or a numpy array")

    if not isinstance(audio, _np.ndarray):
        raise TypeError("audio must be a filepath string or a numpy.ndarray")

    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        _write_wav_file(audio, sample_rate, tmp.name)
        segments, info = model.transcribe(tmp.name, language=language)
        return "".join(segment.text for segment in segments)
    finally:
        if tmp is not None:
            try:
                os.remove(tmp.name)
            except Exception:
                pass


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