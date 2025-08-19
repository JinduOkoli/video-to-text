from faster_whisper import WhisperModel

def transcribe_audio(audio_path: str):
    audio_text = ""
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio=audio_path)

    for segment in segments:
        audio_text += segment

    return audio_text
