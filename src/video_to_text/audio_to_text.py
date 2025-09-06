import logging

from faster_whisper import WhisperModel
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_device():
    try:
        import torch
    except ModuleNotFoundError:
        logger.warning("PyTorch not installed. Using CPU only.")
        return "cpu"

    # Check GPU availability
    if torch.cuda.is_available():
        logger.info("Using CUDA GPU")
        return "cuda"
    else:
        logger.info("Using CPU")
        return "cpu"

def transcribe_audio(audio_path: str, video: Dict, output_dir: Path, save_as_text: Optional[bool] = False) -> str:
    device = get_device()

    if device == "cpu":
        compute_type = "int8"
    else:
        compute_type = "float16"

    model = WhisperModel(model_size_or_path="medium", device=device, compute_type=compute_type)
    logger.info("Starting transcription ...")
    segments, info = model.transcribe(audio=audio_path, log_progress=True)
    logger.info("Successfully transcribed audio. Compiling segments ...")

    filepath = output_dir / f"{video["PublishedAt"]}_{video["Title"]}].txt"

    audio_text = " ".join(s.text for s in segments)

    if save_as_text:
        write_segments_to_file(audio_text=audio_text, filepath=filepath)

    return audio_text

def write_segments_to_file(audio_text: str, filepath: Path):
    logger.info(f"Writing full text to file: {filepath} ...")
    try:
        with open(filepath, 'w') as file:
            file.write(audio_text)

    except OSError as e:
        raise OSError(f"Unable to write to file: {e}")
