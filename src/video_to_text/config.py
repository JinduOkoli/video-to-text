from pathlib import Path
from platformdirs import user_data_dir
import os

from video_to_text.constants import DB_NAME
from video_to_text.utils import get_api_key

API_KEY = get_api_key("YOUTUBE_API_KEY")

APP_NAME = "video_to_text"

def resolve_base_dir(base_dir: Path | None = None) -> Path:
    return Path(
        base_dir
        or os.getenv("VIDEO_TO_TEXT_HOME")
        or user_data_dir(APP_NAME)
    )

def resolve_db_path(db_path: Path | None = None) -> Path:
    base = Path(
        db_path
        or os.getenv("VIDEO_TO_TEXT_DB_PATH")
        or user_data_dir(APP_NAME)
    )

    db_dir = create_dir("db", base_dir=base)
    return db_dir / DB_NAME

def create_dir(name: str, base_dir: Path | None = None) -> Path:
    base = resolve_base_dir(base_dir)
    path = base / name
    path.mkdir(parents=True, exist_ok=True)
    return path
