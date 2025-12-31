import torch
import numpy as np
import sounddevice as sd
import queue
import threading
from faster_whisper import WhisperModel
import os
import tempfile
import wave

SAMPLE_RATE = 16000
CHUNK_DURATION = 0.03  # 30ms chunks for real-time
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

# Load Silero VAD (on first run)
# torch.hub.load may return either (model, utils) or just model depending on environment.
# Handle both cases to avoid "object is not iterable" errors.
_hub_res = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                         model='silero_vad',
                         force_reload=False,
                         onnx=False)
if isinstance(_hub_res, tuple) or isinstance(_hub_res, list):
    model = _hub_res[0]
    utils = _hub_res[1] if len(_hub_res) > 1 else None
else:
    model = _hub_res
    utils = None

# Optional helpers (may be None if utils wasn't returned)
# Safely extract helpers only if utils is an iterable (list/tuple). Avoid
# unpacking None which raises "NoneType' object is not iterable".
get_speech_timestamps = None
read_audio = None
if isinstance(utils, (list, tuple)):
    # Pad to avoid IndexError if utils is shorter than expected
    padded = list(utils) + [None] * 5
    get_speech_timestamps = padded[0]
    read_audio = padded[2]

class VADListener:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.audio_buffer = []
        self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")  # Fast STT

    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy().flatten())

    def listen(self, callback):
        """Listen with VAD; call callback with transcribed text when done speaking."""
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback, blocksize=CHUNK_SIZE):
            print("Emily's listening... (speak now!)")
            while True:
                try:
                    audio_chunk = self.audio_queue.get(timeout=1)
                    self.audio_buffer.extend(audio_chunk)
                    
                    # VAD on buffer
                    if len(self.audio_buffer) >= SAMPLE_RATE:  # Process 1s chunks
                        buffer_np = np.array(self.audio_buffer[-SAMPLE_RATE:], dtype=np.float32)

                        # Determine if there's speech in the buffer.
                        # Prefer the helper from utils when available; fallback to
                        # calling the model's forward if possible.
                        speech_active = False
                        if callable(get_speech_timestamps):
                            try:
                                timestamps = get_speech_timestamps(buffer_np, model, sampling_rate=SAMPLE_RATE)
                                speech_active = bool(timestamps)
                            except Exception:
                                speech_active = False
                        else:
                            try:
                                try:
                                    # Prefer calling the model directly if it's callable
                                    if callable(model):
                                        preds = model(torch.from_numpy(buffer_np))
                                    else:
                                        # Safely get a 'forward' attribute without static-type
                                        # checkers complaining about unknown attributes on 'object'.
                                        forward = getattr(model, "forward", None)
                                        if callable(forward):
                                            preds = forward(torch.from_numpy(buffer_np))
                                        else:
                                            preds = None
                                except Exception:
                                    preds = None

                                if isinstance(preds, torch.Tensor):
                                    speech_probs = preds.detach().cpu().numpy()
                                    speech_active = float(np.mean(speech_probs)) > 0.5
                                else:
                                    speech_active = False
                            except Exception:
                                speech_active = False

                        # Detect speech start/end using boolean flag
                        if speech_active and not self.is_speaking:
                            self.is_speaking = True
                            print("Speaking...")
                            self.audio_buffer = []  # Reset for utterance
                        elif (not speech_active) and self.is_speaking:
                            self.is_speaking = False
                            print("Done speaking.")
                            # Transcribe buffer
                            if len(self.audio_buffer) > SAMPLE_RATE / 2:  # Min length
                                text = self._transcribe_utterance(np.array(self.audio_buffer))
                                if text:
                                    callback(text)
                            self.audio_buffer = []
                    
                except queue.Empty:
                    if self.is_speaking and len(self.audio_buffer) > 0:
                        # End of input: Transcribe
                        text = self._transcribe_utterance(np.array(self.audio_buffer))
                        if text:
                            callback(text)
                    break

    def _transcribe_utterance(self, audio: np.ndarray):
        # Save temp for Whisper
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio_int16 = (audio * 32767).astype(np.int16)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())
        
        segments, _ = self.whisper_model.transcribe(tmp.name)
        os.remove(tmp.name)
        return " ".join(seg.text for seg in segments).strip()