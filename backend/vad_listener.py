import numpy as np
import queue
import threading
import os
import tempfile
import wave
import time  # NEW: For retry delays

# Optional dependencies (torch, sounddevice, faster_whisper)
try:
    import sounddevice as sd
except Exception:
    sd = None

try:
    import torch
except Exception:
    torch = None

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

SAMPLE_RATE = 16000
CHUNK_DURATION = 0.03  # 30ms chunks for real-time
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

class VADListener:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.audio_buffer = []
        self.whisper_model = None
        self.model = None
        self.get_speech_timestamps = None

        # Lazy-load heavy models only when needed
        if WhisperModel is not None:
            try:
                self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            except Exception:
                self.whisper_model = None

        if torch is not None:
            try:
                _hub_res = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, onnx=False)
                if isinstance(_hub_res, (tuple, list)):
                    self.model = _hub_res[0]
                    utils = _hub_res[1] if len(_hub_res) > 1 else None
                else:
                    self.model = _hub_res
                    utils = None
                if isinstance(utils, (list, tuple)):
                    padded = list(utils) + [None] * 5
                    self.get_speech_timestamps = padded[0]
            except Exception:
                self.model = None
                self.get_speech_timestamps = None

    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy().flatten())

    def listen(self, callback):
        if sd is None:
            raise RuntimeError("sounddevice not available; install with 'pip install sounddevice'")

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback, blocksize=CHUNK_SIZE):
            # REMOVED: print("Emily's listening... (speak now!)") - Now in main()
            silence_count = 0  # Counter for occasional no-speech signal
            while True:  # Continuous loop, no break on Empty
                try:
                    audio_chunk = self.audio_queue.get(timeout=1)
                    self.audio_buffer.extend(audio_chunk)

                    # VAD on buffer
                    if len(self.audio_buffer) >= SAMPLE_RATE:  # Process 1s chunks
                        buffer_np = np.array(self.audio_buffer[-SAMPLE_RATE:], dtype=np.float32)

                        speech_active = False
                        if callable(self.get_speech_timestamps):
                            try:
                                timestamps = self.get_speech_timestamps(buffer_np, self.model, sampling_rate=SAMPLE_RATE)
                                speech_active = bool(timestamps)
                            except Exception:
                                speech_active = False
                        else:
                            speech_active = False

                        if speech_active and not self.is_speaking:
                            self.is_speaking = True
                            print("Speaking...")
                            self.audio_buffer = []  # Reset for utterance
                            silence_count = 0  # Reset silence
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
                    # No break - Continue listening
                    if not self.is_speaking:
                        silence_count += 1
                        if silence_count % 10 == 0:  # Every ~10s of silence, signal once
                            callback(None)  # Triggers "Speech not detected." in on_utterance
                    else:
                        # If was speaking but queue empty (rare), transcribe pending
                        if len(self.audio_buffer) > 0:
                            text = self._transcribe_utterance(np.array(self.audio_buffer))
                            if text:
                                callback(text)
                            self.audio_buffer = []
                            self.is_speaking = False

    def _transcribe_utterance(self, audio: np.ndarray):
        if self.whisper_model is None:
            raise RuntimeError("Whisper model not available; install faster-whisper")

        # NEW: Early return for very short audio (noise)
        if len(audio) < SAMPLE_RATE * 0.5:
            return ""

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        try:
            audio_int16 = (audio * 32767).astype(np.int16)
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_int16.tobytes())
                wf.close()  # FIXED: Explicitly close wave writer

            segments, _ = self.whisper_model.transcribe(tmp.name)
            text = " ".join(seg.text for seg in segments).strip()
        finally:
            tmp.close()  # FIXED: Close temp file handle

        # FIXED: Windows-safe delete with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                os.remove(tmp.name)
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Wait for lock release
                else:
                    print(f"WARNING: Could not delete temp file {tmp.name} (manual cleanup needed).")

        return text