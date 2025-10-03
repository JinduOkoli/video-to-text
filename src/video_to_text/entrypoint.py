import click
import logging
from pathlib import Path
from platformdirs import user_data_dir

from video_to_text.constants import DB_NAME
from video_to_text.cli.callbacks import parse_max_videos
from video_to_text.core import run_transcription

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--channel-name", "-c",
    help="Name of the YouTube channel"
)
@click.option(
    "--video-id", "-v",
    help="ID of the video to be retrieved"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(user_data_dir(appname="video_to_text")),
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
def main(channel_name, video_id, output_dir, max_videos, min_duration, max_duration, start_date, end_date, save_as_text):
    click.echo("Starting video transcription...")

    if channel_name and video_id:
        raise click.UsageError("You must provide either --channel-name or --video-id and not both.")

    if not channel_name and not video_id:
        raise click.UsageError("You must provide either --channel-name or --video-id.")

    run_transcription(channel_name=channel_name,
                      video_id=video_id,
                      output_dir=output_dir,
                      max_videos=max_videos,
                      min_duration=min_duration,
                      max_duration=max_duration,
                      start_date=start_date,
                      end_date=end_date,
                      save_as_text=save_as_text)

    if save_as_text:
        click.echo(f"Text files saved under {output_dir}")

    click.echo(f"Done! {DB_NAME} located at {output_dir}")

if __name__ == "__main__":
    main()
