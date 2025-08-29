import logging
from faster_whisper import WhisperModel
from pathlib import Path

def transcribe_audio(audio_path: str, title: str, output_dir: Path):
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio=audio_path)
    logging.info("Successfully transcribed audio. Writing to file ...")

    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{title}.txt"
    filepath.unlink(missing_ok=True)

    for segment in segments:
        write_segments_to_file(segment=segment.text, filepath=filepath)

def write_segments_to_file(segment: str, filepath: Path):
    try:
        with open(filepath, 'a') as file:
            file.write(segment + "\n")

    except OSError as e:
        raise OSError(f"Unable to write to file: {e}")
