import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import VideoUnavailable, CouldNotRetrieveTranscript

from video_to_text.audio_to_text import transcribe_audio
from video_to_text.config import API_KEY
from video_to_text.constants import DB_NAME
from video_to_text.database import init_db, save_to_db
from video_to_text.exceptions import YouTubeTranscribeException, YouTubeCaptionException
from video_to_text.get_yt_videos import get_channel_id, get_channel_videos, get_single_video
from video_to_text.video_to_audio import download_audio

logger = logging.getLogger(__name__)

def run_transcription(channel_name: str = None,
                      video_id: str = None,
                      output_dir: Path = None,
                      max_videos: int = None,
                      min_duration: int = None,
                      max_duration: int = None,
                      start_date: datetime = None,
                      end_date: datetime = None,
                      save_as_text: bool = False) -> List | None:
    """
    Main logic that retrieves YouTube videos, downloads, transcribes abd saves in DB

    :param channel_name: Name of the YouTube channel
    :param video_id: ID of the video to be retrieved
    :param output_dir: Directory to save transcribed text files
    :param max_videos: Max number of videos (integer) to fetch entire channel
    :param min_duration: Minimum duration of video to be retrieved from channel
    :param max_duration: Maximum duration of video to be retrieved from channel
    :param start_date: Only include videos published on or after this date (YYYY-MM-DD)
    :param end_date: Only include videos published on or before this date (YYYY-MM-DD)
    :param save_as_text: Save transcribed audio in .text file
    :return: List containing video data
    """
    video_data: List = []
    ytt_api = YouTubeTranscriptApi()

    output_dir.mkdir(parents=True, exist_ok=True)

    db_file = output_dir/DB_NAME
    # Initialize DB
    init_db(db_file=db_file)

    if video_id:
        videos = get_single_video(video_id=video_id,
                                  api_key=API_KEY)
    else:
        channel_id = get_channel_id(channel_name, API_KEY)
        videos = get_channel_videos(channel_id=channel_id,
                                    api_key=API_KEY,
                                    max_num_of_videos=max_videos,
                                    min_duration=min_duration,
                                    max_duration=max_duration,
                                    start_date=start_date,
                                    end_date=end_date)

    for video in videos:
        tempdir = tempfile.TemporaryDirectory()

        try:
            fetched_transcript = ytt_api.fetch(video.get("Id"))
            audio_text = " ".join([entry.text for entry in fetched_transcript])

        except VideoUnavailable:
            logger.error("Video unavailable: %s", video_id)
            return None

        except CouldNotRetrieveTranscript as e:
            logger.warning(f"Captions unavailable for {video_id}: {e} — falling back to audio")
            try:

                audio_path = download_audio(youtube_url=video["URL"], tempdir=tempdir.name)
                audio_text = transcribe_audio(audio_path=audio_path,
                                              video=video,
                                              output_dir=output_dir,
                                              save_as_text=save_as_text)

            except Exception as e:
                logger.exception(f"Audio fallback failed for {video_id}: {e}")
                raise YouTubeTranscribeException(e)

        except Exception as e:
            logger.exception(f"Unexpected error for {video_id}: {e}")
            raise YouTubeCaptionException(e)

        db_id = save_to_db(video_url=video["URL"],
                           title=video["Title"],
                           published_at=video["PublishedAt"],
                           audio_text=audio_text,
                           db_file=db_file)
        if db_id:
            video["id"] = db_id

        video_data.append(video)
        tempdir.cleanup()

    return video_data
