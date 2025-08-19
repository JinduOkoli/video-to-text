import isodate
import requests

from typing import List
from constants import YOUTUBE_API_URL, MIN_VIDEO_DURATION

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
        resp = requests.get(url=f"{YOUTUBE_API_URL}/search", params=params).json()
        items = resp.get("items", [])
        if not items:
            raise ValueError("Channel not found.")

        return items[0]["snippet"]["channelId"]

    except requests.RequestException as e:
        raise requests.RequestException(f"An error occurred while retrieving the channel ID: {e}")


def get_channel_videos(channel_id: str,  api_key: str, max_num_of_videos=2) -> List:
    videos = []
    page_token = None

    while True:
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": 50,
            "order": "date",
            "type": "video",
            "key": api_key
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(url=f"{YOUTUBE_API_URL}/search", params=params).json()

        for item in resp.get("items", []):
            video_id = item["id"]["videoId"]
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
