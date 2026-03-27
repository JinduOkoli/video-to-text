from pathlib import Path
from pydantic import BaseModel, conint, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime

# ----- Video transcription -----
class VideoTranscriptionRequest(BaseModel):
    video_id: str
    output_dir: Optional[Path] = None

# ----- Channel transcription -----
class ChannelTranscriptionRequest(BaseModel):
    channel_name: str
    output_dir: Optional[Path] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_videos: Optional[conint(gt=0)] = 10
    min_duration: Optional[conint(ge=0)] = None
    max_duration: Optional[conint(gt=0)] = None

class TranscriptionResult(BaseModel):
    video_url: HttpUrl
    title: str
    published: datetime
    status: str

class TranscriptionResponse(TranscriptionResult):
    db_id: int

    model_config = ConfigDict(from_attributes=True)
