from faster_whisper import WhisperModel

print("Loading Whisper model...")

model = WhisperModel("small", device="cpu", compute_type="int8")

print("Transcribing audio...")

segments, info = model.transcribe(
    "test.wav",
    language="en",  # change to "en" for English
    beam_size=5
)

print("Detected language:", info.language)

for segment in segments:
    print("Text:", segment.text)
