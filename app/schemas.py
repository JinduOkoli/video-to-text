from pydantic import BaseModel, conint, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime

# ----- Channel transcription -----
class ChannelTranscriptionRequest(BaseModel):
    channel_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_videos: Optional[conint(gt=0)] = 10
    min_duration: Optional[conint(ge=0)] = None
    max_duration: Optional[conint(gt=0)] = None
    save_as_text: Optional[bool] = False

class TranscriptionResult(BaseModel):
    video_url: HttpUrl
    title: str
    published: datetime
    status: str

class ChannelResponse(TranscriptionResult):
    db_id: int

    model_config = ConfigDict(from_attributes=True)
