import logging

from fastapi import FastAPI, HTTPException
from pathlib import Path
from platformdirs import user_data_dir

from .schemas import ChannelTranscriptionRequest
from video_to_text.core import run_transcription

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI()

OUTPUT_DIR = Path(user_data_dir(appname="video-to-text"))

@app.post("/transcribe/channel")
def transcribe_channel(payload: ChannelTranscriptionRequest):
    try:
        video_data = run_transcription(
                        channel_name=payload.channel_name,
                        output_dir=Path(OUTPUT_DIR),
                        max_videos=payload.max_videos,
                        min_duration=payload.min_duration,
                        max_duration=payload.max_duration,
                        start_date=payload.start_date,
                        end_date=payload.end_date,
                        save_as_text=payload.save_as_text
                    )
        logger.info(f"Successfully transcribed {len(video_data)} video(s) located at {OUTPUT_DIR}")
        return {"transcriptions": video_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


