import csv
import isodate
import requests
import os
import subprocess

from constants import YOUTUBE_API_URL, MIN_VIDEO_DURATION
from utils import get_api_key

API_KEY = get_api_key("YOUTUBE_API_KEY")


def get_channel_id(channel_name: str) -> str:
    """
    Retrieves channel ID based on channel name provided

    :param channel_name: Name of the channel
    :return: string containing channel ID
    """
    if channel_name.startswith("@"):
        channel_name = channel_name[1:]

    params = {
        "part": "snippet",
        "q": channel_name,
        "type": "channel",
        "maxResults": 1,
        "key": API_KEY
    }

    try:
        resp = requests.get(url=f"{YOUTUBE_API_URL}/search", params=params).json()
        items = resp.get("items", [])
        if not items:
            raise ValueError("Channel not found.")

        return items[0]["snippet"]["channelId"]

    except requests.RequestException as e:
        raise requests.RequestException("An error occurred while retrieving the channel ID")


def get_channel_videos(channel_id: str, max_num_of_videos=2):
    videos = []
    page_token = None

    while True:
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": 50,
            "order": "date",
            "type": "video",
            "key": API_KEY
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(url=f"{YOUTUBE_API_URL}/search", params=params).json()

        for item in resp.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"]
            duration = get_video_duration(video_id)

            if duration < MIN_VIDEO_DURATION:
                continue

            videos.append({
                "Title": title,
                "URL": f"https://www.youtube.com/watch?v={video_id}",
                "PublishedAt": published_at
            })

            if len(videos) == max_num_of_videos:
                return videos

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return videos

def get_video_duration(video_id: str) -> int:
    """
    Get duration of the Youtube video

    :param video_id: ID of the Youtube video
    :return: str
    """
    params = {
        "part": "contentDetails",
        "id": video_id,
        "key": API_KEY
    }
    resp = requests.get(url=f"{YOUTUBE_API_URL}/videos", params=params).json()
    items = resp.get("items", [])
    if not items:
        return 0

    duration = items[0]["contentDetails"]["duration"]
    return parse_duration(duration)

def parse_duration(duration: str) -> int:
    """
    Convert duration from  ISO 8601 duration format to seconds

    :param duration: Duration in ISO 8601 format
    :return: duration in seconds
    """
    duration_str = isodate.parse_duration(duration)
    return int(duration_str.total_seconds())


def download_audio(video_url, output_dir="downloads"):
    """Download audio from YouTube video as MP3 using yt-dlp."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"[🎵] Downloading audio for {video_url} ...")
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "mp3",
        "-o", f"{output_dir}/%(title)s.%(ext)s", video_url
    ], check=True)

def save_to_csv(videos, filename="youtube_videos.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "URL", "PublishedAt"])
        writer.writeheader()
        writer.writerows(videos)
    print(f"[✅] Saved {len(videos)} videos to {filename}")

def transcribe_audio(audio_file, model="medium"):
    print("[2/3] Transcribing audio with Whisper...")
    subprocess.run([
        "whisper", audio_file, "--model", model, "--output_format", "txt"
    ], check=True)
