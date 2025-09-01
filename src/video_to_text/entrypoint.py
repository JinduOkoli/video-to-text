import tempfile
import click
import logging
from pathlib import Path

from video_to_text.audio_to_text import transcribe_audio
from video_to_text.config import API_KEY
from video_to_text.get_yt_videos import get_channel_id, get_channel_videos
from video_to_text.video_to_audio import download_audio
from video_to_text.cli.callbacks import parse_max_videos

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--channel-name", "-c",
    required=True,
    help="Name of the YouTube channel"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path.home() / "video_to_text",   # default to ~/video_to_text
    show_default=True,        # shows [~] in help
    help="Directory to save transcribed text files"
)
@click.option(
    "--max-videos", "-m",
    callback=parse_max_videos,
    default=10,
    show_default=True,
    help="Max number of videos (integer) or 'all' to fetch entire channel."
)
@click.option(
    "--min-duration", "-d",
    type=int,
    default=900,
    show_default=True,
    help="Minimum duration of video to be retrieved from channel."
)
@click.option(
    "--start-date", "-s",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Only include videos published on or after this date (YYYY-MM-DD)"
)
@click.option(
    "--end-date", "-e",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Only include videos published on or before this date (YYYY-MM-DD)"
)
@click.help_option("-h", "--help")
def main(channel_name, output_dir, max_videos, min_duration, start_date, end_date):
    click.echo("Starting video transcription...")
    tempdir = tempfile.TemporaryDirectory()

    channel_id = get_channel_id(channel_name, API_KEY)
    videos = get_channel_videos(channel_id=channel_id,
                                api_key=API_KEY,
                                max_num_of_videos=max_videos,
                                min_duration=min_duration,
                                start_date=start_date,
                                end_date=end_date)

    for video in videos:
        audio_name = download_audio(youtube_url=video["URL"], tempdir=tempdir.name)
        audio_path = f"{tempdir.name}/{audio_name}"
        transcribe_audio(audio_path=audio_path, title=video["Title"], output_dir=output_dir)

    click.echo(f"Done! Files located at {output_dir}")

    tempdir.cleanup()

if __name__ == "__main__":
    main()
