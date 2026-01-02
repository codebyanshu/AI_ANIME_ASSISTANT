import random
import numpy as np

VOICE = "voices/my_voice.wav"  # Your cloned voice
OUTPUT_PATH = "output/response.wav"

_tts_instance = None
_sf = None
_sd = None

def _get_tts():
    global _tts_instance
    if _tts_instance is not None:
        return _tts_instance
    try:
        from TTS.api import TTS
    except Exception:
        raise RuntimeError("TTS package not available; install with 'pip install TTS'")
    _tts_instance = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    return _tts_instance

def _ensure_audio_libs():
    global _sf, _sd
    if _sf is None:
        try:
            import soundfile as sf
            _sf = sf
        except Exception:
            _sf = None
    if _sd is None:
        try:
            import sounddevice as sd
            _sd = sd
        except Exception:
            _sd = None

def add_pauses(text: str, pause_prob: float) -> str:
    """Add natural pauses/fillers for friendly feel."""
    if random.random() < pause_prob:
        fillers = ["um...", "like...", "you know?", "haha"]
        text = random.choice(fillers) + " " + text
    if "..." not in text and random.random() < 0.2:
        text = text.replace('.', '... ')
    return text

def speak(text: str, settings: dict):
    """Generate and (optionally) play audio. Requires TTS and sound libraries."""
    _ensure_audio_libs()
    tts = _get_tts()
    enhanced_text = add_pauses(text, settings.get("pause_prob", 0.1))

    _tts_out = settings.get("output_path", OUTPUT_PATH)
    tts.tts_to_file(
        text=enhanced_text,
        speaker_wav=settings.get("speaker_wav", VOICE),
        language=settings.get("language", "en"),
        file_path=_tts_out,
        temperature=settings.get("temperature", 0.7),
    )

    if _sf is None:
        return

    data, sr = _sf.read(_tts_out)
    speed_factor = settings.get("speed", 1.0)
    if speed_factor <= 0:
        speed_factor = 1.0
    new_len = int(len(data) / speed_factor)
    resampled = np.interp(np.linspace(0, len(data)-1, new_len), np.arange(len(data)), data)

    if settings.get("pitch_shift", 0) != 0:
        shift_samples = int(len(resampled) * settings["pitch_shift"] / 12)
        resampled = np.roll(resampled, shift_samples)

    _sf.write(_tts_out, resampled, int(sr / speed_factor))

    if _sd is not None:
        play_data, play_sr = _sf.read(_tts_out)
        _sd.play(play_data, play_sr)
        _sd.wait()