import os
import assemblyai as aai
import numpy as np
import wave
import tempfile

# Set API key globally (or per transcriber)
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# ... (rest of your VADListener class unchanged)

def VADListener(self, audio: np.ndarray):
    if len(audio) < self.SAMPLE_RATE * 0.5:  # Assuming self.SAMPLE_RATE is defined (e.g., 16000)
        return ""

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        # Write audio to WAV file
        audio_int16 = (audio * 32767).astype(np.int16)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        # Configure transcription (add more options if needed, e.g., speaker_labels=True)
        config = aai.TranscriptionConfig(
            language_code="en",  # Or "auto" for detection
            punctuate=True,
            format_text=True
        )

        # Transcribe - SDK handles upload and polling
        transcript = aai.Transcriber().transcribe(tmp.name, config=config)

        # Check for errors
        if transcript.status == aai.TranscriptStatus.error:
            print(f"AssemblyAI error: {transcript.error}")
            return ""

        text = transcript.text.strip() if transcript.text else ""
    except Exception as e:
        print(f"STT API error: {e}")
        text = ""
    finally:
        try:
            os.unlink(tmp.name)
        except:
            pass

    return text