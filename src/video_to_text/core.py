import tempfile
from datetime import datetime
from pathlib import Path
from typing import List

from video_to_text.audio_to_text import transcribe_audio
from video_to_text.config import API_KEY
from video_to_text.constants import DB_NAME
from video_to_text.database import init_db, save_to_db
from video_to_text.get_yt_videos import get_channel_id, get_channel_videos
from video_to_text.video_to_audio import download_audio

def run_transcription(channel_name: str,
                      output_dir: Path,
                      max_videos: int,
                      min_duration: int,
                      max_duration: int,
                      start_date: datetime,
                      end_date: datetime,
                      save_as_text: bool) -> List:
    """
    Main logic that retrieves YouTube videos, downloads, transcribes abd saves in DB

    :param channel_name: Name of the YouTube channel
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

    output_dir.mkdir(parents=True, exist_ok=True)

    db_file = output_dir/DB_NAME
    # Initialize DB
    init_db(db_file=db_file)

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
        audio_path = download_audio(youtube_url=video["URL"], tempdir=tempdir.name)
        audio_text = transcribe_audio(audio_path=audio_path,
                                      video=video,
                                      output_dir=output_dir,
                                      save_as_text=save_as_text)

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
