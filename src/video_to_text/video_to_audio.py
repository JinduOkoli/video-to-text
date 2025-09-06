import yt_dlp
import logging
from tenacity import (retry, stop_after_attempt, wait_exponential,
                      before_log, after_log)

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=2),
       before=before_log(logger, logging.INFO),
       after=after_log(logger, logging.INFO),
       reraise=True)
def download_audio(youtube_url, tempdir) -> str:
    """
    Download audio file from YouTube URL

    :param youtube_url: YouTube URL
    :param tempdir: Temporary directory
    :return: str containing filename
    """
    ydl_opts = {
        'format': '140/251/bestaudio',
        'outtmpl': f'{tempdir}/%(title)s-%(id)s.%(ext)s',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio',
             'preferredcodec': 'mp3',
             'preferredquality': '192'}
        ]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url)

        for fmt in info.get("requested_downloads", []):
            logger.debug(f"Chosen format: id={fmt.get("format_id")} note={fmt.get("format_note")}")

        output_path = ydl.prepare_filename(info)
        file_path = yt_dlp.utils.replace_extension(output_path, "mp3")
    return file_path
