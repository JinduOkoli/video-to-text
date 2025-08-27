import logging

import isodate
import requests

from typing import List

from video_to_text.constants import YOUTUBE_API_URL, MIN_VIDEO_DURATION
from video_to_text.exceptions import YouTubeAPIException

logger = logging
logger.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def get_channel_id(channel_name: str, api_key: str) -> str:
    """
    Retrieves channel ID based on channel name provided

    :param channel_name: Name of the channel
    :param api_key:
    :return: string containing channel ID
    """
    if channel_name.startswith("@"):
        channel_name = channel_name[1:]

    params = {
        "part": "snippet",
        "q": channel_name,
        "type": "channel",
        "maxResults": 1,
        "key": api_key
    }

    try:
        resp = requests.get(url=f"{YOUTUBE_API_URL}/search", params=params)

        if not resp.ok:
            extract_error_message(resp)

        items = resp.json().get("items", [])
        if not items:
            raise ValueError("Channel not found.")

        return items[0]["snippet"]["channelId"]

    except (requests.HTTPError, ValueError) as e:
        raise YouTubeAPIException(e)

def get_uploads_playlist_id(channel_id: str, api_key: str) -> str:
    """
    Get the 'uploads' playlist ID for a channel

    :param channel_id: ID of the YouTube channel
    :param api_key: API key for authentication
    :return: str
    """
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": api_key
    }
    try:
        resp = requests.get(f"{YOUTUBE_API_URL}/channels", params=params)

        if not resp.ok:
            extract_error_message(resp)

        items = resp.json().get("items", [])
        if not items:
            raise ValueError("Could not fetch channel details")

        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    except (requests.HTTPError, ValueError, KeyError) as e:
        logger.error(f"An error occurred while retrieving Upload ID: {e}")
        raise YouTubeAPIException(e)

def get_channel_videos(channel_id: str,  api_key: str, max_num_of_videos=2) -> List:
    videos = []
    page_token = None

    uploads_playlist_id = get_uploads_playlist_id(channel_id, api_key)

    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": uploads_playlist_id,
            "maxResults": 50,
            "key": api_key
        }
        if page_token:
            params["pageToken"] = page_token

        try:
            resp = requests.get(f"{YOUTUBE_API_URL}/playlistItems", params=params).json()

            for item in resp.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                title = item["snippet"]["title"]
                published_at = item["snippet"]["publishedAt"]
                duration = get_video_duration(video_id=video_id, api_key=api_key)

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

        except (requests.HTTPError, ValueError, KeyError) as e:
            raise YouTubeAPIException(e)

    return videos

def get_video_duration(video_id: str, api_key: str) -> int:
    """
    Get duration of the YouTube video

    :param video_id: ID of the YouTube video
    :param api_key: API key for authentication
    :return: str
    """
    params = {
        "part": "contentDetails",
        "id": video_id,
        "key": api_key
    }
    try:
        resp = requests.get(url=f"{YOUTUBE_API_URL}/videos", params=params)

        if not resp.ok:
            extract_error_message(resp)

        items = resp.json().get("items", [])
        if not items:
            return 0

        duration = items[0]["contentDetails"]["duration"]
        return parse_duration(duration)

    except (requests.HTTPError, ValueError) as e:
        raise YouTubeAPIException(e)

def parse_duration(duration: str) -> int:
    """
    Convert duration from  ISO 8601 duration format to seconds

    :param duration: Duration in ISO 8601 format
    :return: duration in seconds
    """
    duration_str = isodate.parse_duration(duration)
    return int(duration_str.total_seconds())


def extract_error_message(resp):
    # Extract detailed error message from YouTube API
    error_message = resp.json().get("error", {}).get("message")
    if error_message:
        raise ValueError(f"YouTube API error: {error_message}")

    resp.raise_for_status()
