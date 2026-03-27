import logging
import tempfile
from datetime import datetime
from pathlib import Path
from slugify import slugify
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import VideoUnavailable, CouldNotRetrieveTranscript

from video_to_text.audio_to_text import transcribe_audio
from video_to_text.config import API_KEY, create_dir, resolve_db_path
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
                      end_date: datetime = None) -> List | None:
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
    :return: List containing video data
    """
    video_data: List = []
    ytt_api = YouTubeTranscriptApi()

    transcripts_dir = create_dir("transcripts", base_dir=output_dir)

    db_filepath = resolve_db_path()
    # Initialize DB
    init_db(db_filepath=db_filepath)

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
        video_id = video.get("Id")
        logger.info(f"Attempting to transcribe video with URL: {video.get("URL")}")
        tempdir = tempfile.TemporaryDirectory()

        try:
            fetched_transcript = ytt_api.fetch(video_id)
            audio_text = " ".join([entry.text for entry in fetched_transcript])

        except VideoUnavailable:
            logger.error("Video unavailable: %s", video_id)
            return None

        except CouldNotRetrieveTranscript as e:
            logger.warning(f"Captions unavailable for {video_id}: {e} — falling back to audio")
            try:

                audio_path = download_audio(youtube_url=video["URL"], tempdir=tempdir.name)
                audio_text = transcribe_audio(audio_path=audio_path)

            except Exception as e:
                logger.exception(f"Audio fallback failed for {video_id}: {e}")
                raise YouTubeTranscribeException(e)

        except Exception as e:
            logger.exception(f"Unexpected error for {video_id}: {e}")
            raise YouTubeCaptionException(e)

        safe_title = f"{video_id}_{slugify(video.get('Title'))[:80]}.txt"
        transcript_path = transcripts_dir / safe_title

        write_segments_to_file(audio_text=audio_text, filepath=transcript_path)
        logger.info(f"File located at {transcript_path}")
        video["transcript_path"] = transcript_path

        db_id = save_to_db(video_url=video["URL"],
                           title=video["Title"],
                           published_at=video["PublishedAt"],
                           transcript_path=str(transcript_path),
                           db_filepath=db_filepath)
        if db_id:
            video["id"] = db_id

        video_data.append(video)
        tempdir.cleanup()

    logger.info(f"DB file located at {db_filepath}")
    return video_data

def write_segments_to_file(audio_text: str, filepath: Path):
    logger.info(f"Writing full text to file: {filepath} ...")
    try:
        with open(filepath, 'w') as file:
            file.write(audio_text)

    except OSError as e:
        raise OSError(f"Unable to write to file: {e}")
