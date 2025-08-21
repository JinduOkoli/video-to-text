import logging
from faster_whisper import WhisperModel
from pathlib import Path

from video_to_text.constants import TRANSCRIPT_LOCATION

def transcribe_audio(audio_path: str, title: str):
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio=audio_path)
    logging.info("Successfully transcribed audio. Writing to file ...")

    folder_path = Path(TRANSCRIPT_LOCATION)
    folder_path.mkdir(parents=True, exist_ok=True)
    filepath = folder_path / f"{title}.txt"
    filepath.unlink(missing_ok=True)

    for segment in segments:
        write_segments_to_file(segment=segment.text, filepath=filepath)

def write_segments_to_file(segment: str, filepath: Path):
    try:
        with open(filepath, 'a') as file:
            file.write(segment + "\n")

    except OSError as e:
        raise OSError(f"Unable to write to file: {e}")
