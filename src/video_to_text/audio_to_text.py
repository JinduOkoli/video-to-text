import logging

from faster_whisper import WhisperModel

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

def transcribe_audio(audio_path: str) -> str:
    device = get_device()

    if device == "cpu":
        compute_type = "int8"
    else:
        compute_type = "float16"

    model = WhisperModel(model_size_or_path="medium", device=device, compute_type=compute_type)
    logger.info("Starting transcription ...")
    segments, info = model.transcribe(audio=audio_path, log_progress=True)
    logger.info("Successfully transcribed audio. Compiling segments ...")

    audio_text = " ".join(s.text for s in segments)

    return audio_text

