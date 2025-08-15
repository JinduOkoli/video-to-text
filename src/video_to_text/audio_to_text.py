from faster_whisper import WhisperModel

model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, info = model.transcribe("path/to/audio")

for segment in segments:
    print(segment.text)