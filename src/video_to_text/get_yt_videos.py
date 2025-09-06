import logging

import isodate
import requests

from datetime import datetime
from typing import List, Optional

from video_to_text.constants import YOUTUBE_API_URL
from video_to_text.exceptions import YouTubeAPIException
from video_to_text.helper import convert_iso_to_datetime

logger = logging.getLogger(__name__)

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
        url = f"{YOUTUBE_API_URL}/search"
        resp = requests.get(url=url, params=params)

        if not resp.ok:
            extract_error_message(resp, url)

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
        url = f"{YOUTUBE_API_URL}/channels"
        logger.debug(f"Retrieving Uploads playlist ID from {url}. Channel ID: {channel_id}")
        resp = requests.get(url=url, params=params)

        if not resp.ok:
            extract_error_message(resp, url)

        items = resp.json().get("items", [])
        if not items:
            raise ValueError("Could not fetch channel details")

        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    except (requests.HTTPError, ValueError, KeyError) as e:
        logger.error(f"An error occurred while retrieving Upload ID: {e}")
        raise YouTubeAPIException(e)

def get_channel_videos(channel_id: str,
                       api_key: str,
                       max_num_of_videos: Optional[int],
                       min_duration: Optional[int] = None,
                       max_duration: Optional[int] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List:
    """
    Retrieve videos from YouTube channel

    :param channel_id: ID of the channel
    :param api_key: API key for authentication
    :param max_num_of_videos: Maximum number of videos to retrieve
    :param min_duration: Minimum duration of the video to retrieve
    :param max_duration: Maximum duration of the video to retrieve
    :param start_date: Include videos published on or after this date
    :param end_date: Include videos published on or before this date
    :return: List of videos
    """
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
            url = f"{YOUTUBE_API_URL}/playlistItems"
            logger.debug(f"Retrieving videos from {url}. Playlist ID: {uploads_playlist_id}")
            resp = requests.get(url=url, params=params)

            if not resp.ok:
                extract_error_message(resp, url)

            res = resp.json()
            for item in res.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                title = item["snippet"]["title"]
                published_at = item["snippet"]["publishedAt"]
                duration = get_video_duration(video_id=video_id, api_key=api_key)
                published_at_datetime = convert_iso_to_datetime(published_at)

                if (
                        (min_duration and duration < min_duration)
                        or (max_duration and duration > max_duration)
                        or (start_date and published_at_datetime.date() < start_date.date())
                        or (end_date and published_at_datetime.date() > end_date.date())
                ):
                    continue

                videos.append({
                    "Title": title,
                    "URL": f"https://www.youtube.com/watch?v={video_id}",
                    "PublishedAt": published_at
                })

                if max_num_of_videos and len(videos) == max_num_of_videos:
                    return videos

            page_token = res.get("nextPageToken")
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
    :return: int
    """
    params = {
        "part": "contentDetails",
        "id": video_id,
        "key": api_key
    }
    try:
        url = f"{YOUTUBE_API_URL}/videos"
        logger.debug(f"Retrieving video duration from {url}. Video ID: {video_id}")
        resp = requests.get(url=url, params=params)

        if not resp.ok:
            extract_error_message(resp, url)

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

def extract_error_message(resp, url):
    """
    Extract detailed error message from YouTube API

    :param resp: Response from YouTube API
    :param url: URL request was made to
    :return:
    """
    error_message = resp.json().get("error", {}).get("message")
    if error_message:
        logger.error(f"An error occurred while making request to {url}: {error_message}")
        raise ValueError(f"YouTube API error: {error_message}")

    resp.raise_for_status()
