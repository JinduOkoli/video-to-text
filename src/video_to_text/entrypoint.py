import tempfile
import click
import logging
from pathlib import Path

from video_to_text.audio_to_text import transcribe_audio
from video_to_text.config import API_KEY
from video_to_text.constants import DB_NAME
from video_to_text.get_yt_videos import get_channel_id, get_channel_videos
from video_to_text.video_to_audio import download_audio
from video_to_text.cli.callbacks import parse_max_videos
from video_to_text.database import init_db, save_to_db

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
    "--min-duration", "-n",
    type=int,
    help="Minimum duration of video to be retrieved from channel."
)
@click.option(
    "--max-duration", "-x",
    type=int,
    help="Maximum duration of video to be retrieved from channel."
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
@click.option(
"--save-as-text", "-t",
type=bool,
default=False,
show_default=True,
help="Save transcribed audio in .text file"
)
@click.help_option("-h", "--help")
def main(channel_name, output_dir, max_videos, min_duration, max_duration, start_date, end_date, save_as_text):
    click.echo("Starting video transcription...")

    # Create output dir
    output_dir.mkdir(parents=True, exist_ok=True)
    # Initialize DB
    db_file = output_dir/DB_NAME
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
        save_to_db(video_url=video["URL"],
                   title=video["Title"],
                   published_at=video["PublishedAt"],
                   audio_text=audio_text,
                   db_file=db_file)
        tempdir.cleanup()

    if save_as_text:
        click.echo(f"Text files saved under {output_dir}")

    click.echo(f"Done! {DB_NAME} located at {output_dir}")

    tempdir.cleanup()

if __name__ == "__main__":
    main()
