import tempfile

from video_to_text.audio_to_text import transcribe_audio
from video_to_text.config import API_KEY
from video_to_text.get_yt_videos import get_channel_id, get_channel_videos
from video_to_text.video_to_audio import download_audio
from video_to_text.constants import CHANNEL_NAME, MAX_NUM_OF_VIDEOS


def main():
    tempdir = tempfile.TemporaryDirectory()

    channel_id = get_channel_id(CHANNEL_NAME, API_KEY)
    videos = get_channel_videos(channel_id=channel_id, api_key=API_KEY, max_num_of_videos=MAX_NUM_OF_VIDEOS)

    for video in videos:
        audio_name = download_audio(youtube_url=video["URL"], tempdir=tempdir.name)
        audio_path = f"{tempdir.name}/{audio_name}"
        audio_text = transcribe_audio(audio_path=audio_path, title=video["Title"])

    tempdir.cleanup()

main()