import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ChannelTranscriptionRequest, VideoTranscriptionRequest
from src.video_to_text.config import resolve_base_dir
from src.video_to_text.core import run_transcription

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video-to-Text API",
    description="Transcribe YouTube videos and channels",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allows React app (localhost:5173) to call this API (localhost:8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],       # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],       # allow all headers
)



@app.get("/")
def project_root():
    return {"message": "Welcome to Video-to-Text App!"}


@app.get("/health")
def health_check():
    """
    A simple endpoint to verify the server is running.
    Call GET /health — if you get {"status": "ok"} the server is up.
    """
    return {"status": "ok"}


@app.post("/transcribe/video")
def transcribe_video(payload: VideoTranscriptionRequest):
    """
    Transcribe a single YouTube video by its video ID.

    Example request body:
        {
            "video_id": "LqFc0z-pQTg"
        }
    """
    try:
        base_dir = resolve_base_dir(payload.output_dir)

        video_data = run_transcription(
            video_id=payload.video_id,
            output_dir=base_dir
        )

        if not video_data:
            warning_msg = (
                f"No transcription found for video ID '{payload.video_id}'. "
                "The video may be private, deleted, or have no captions available."
            )
            logger.warning(warning_msg)
            return {"transcriptions": [], "warning": warning_msg}

        logger.info(
            f"Successfully transcribed {len(video_data)} video(s) → {base_dir}"
        )
        return {"transcriptions": video_data}

    except Exception as e:
        logger.error(f"Error transcribing video {payload.video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe/channel")
def transcribe_channel(payload: ChannelTranscriptionRequest):
    """
    Transcribe all (or filtered) videos from a YouTube channel.

    Example request body:
        {
            "channel_name": "MIT OpenCourseWare",
            "max_videos": 10,
            "min_duration": 300,
            "max_duration": 3600,
            "start_date": "2023-01-01",
            "end_date":   "2024-01-01"
        }
    """
    try:
        base_dir = resolve_base_dir(payload.output_dir)

        video_data = run_transcription(
            channel_name=payload.channel_name,
            output_dir=base_dir,
            max_videos=payload.max_videos,
            min_duration=payload.min_duration,
            max_duration=payload.max_duration,
            start_date=payload.start_date,
            end_date=payload.end_date
        )

        if not video_data:
            warning_msg = (
                f"No videos found for channel '{payload.channel_name}'. "
                "The channel may not exist, or no videos matched your filters "
                "(date range, duration, max_videos)."
            )
            logger.warning(warning_msg)
            return {"transcriptions": [], "warning": warning_msg}

        logger.info(
            f"Successfully transcribed {len(video_data)} video(s) → {base_dir}"
        )
        return {"transcriptions": video_data}

    except Exception as e:
        logger.error(f"Error transcribing channel {payload.channel_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
