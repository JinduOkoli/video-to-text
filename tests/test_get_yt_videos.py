import pytest
from unittest.mock import patch

from video_to_text.exceptions import YouTubeAPIException
from video_to_text.get_yt_videos import (
    get_channel_id,
    get_channel_videos,
    parse_duration,
    get_video_duration,
    get_uploads_playlist_id
)

# Update API key to rerun VCR tests
API_KEY = "TEST-API-KEY"

@pytest.mark.vcr
def test_get_channel_id_success():
    channel_id = get_channel_id("GoogleDevelopers", API_KEY)
    assert channel_id == "UC_x5XG1OV2P6uZZ5FSM9Ttw"

@pytest.mark.vcr
def test_get_channel_id_invalid():
    with pytest.raises(YouTubeAPIException) as excinfo:
        get_channel_id("", API_KEY)

    assert "Channel not found" in str(excinfo.value)

def test_parse_duration_seconds():
    assert parse_duration("PT1H2M3S") == 3723
    assert parse_duration("PT15M") == 900
    assert parse_duration("PT0S") == 0

@pytest.mark.vcr
def test_get_uploads_playlist_id_success():
    upload_id = get_uploads_playlist_id("UC_x5XG1OV2P6uZZ5FSM9Ttw", API_KEY)
    assert upload_id == "UU_x5XG1OV2P6uZZ5FSM9Ttw"

@pytest.mark.vcr
def test_get_uploads_playlist_id_failure():
    with pytest.raises(YouTubeAPIException) as excinfo:
        get_uploads_playlist_id("Bad_Channel_Id", API_KEY)

    assert "Could not fetch channel details" in str(excinfo.value)

@pytest.mark.vcr
def test_get_channel_videos_success():
    channel_id = get_channel_id("GoogleDevelopers", API_KEY)
    videos = get_channel_videos(channel_id, API_KEY, max_num_of_videos=2, min_duration=0)

    assert isinstance(videos, list)
    assert len(videos) == 2
    assert all("Title" in v for v in videos)
    assert all("URL" in v for v in videos)
    assert all("PublishedAt" in v for v in videos)

@patch("video_to_text.get_yt_videos.get_uploads_playlist_id")
@patch("video_to_text.get_yt_videos.get_video_duration")
@patch("video_to_text.get_yt_videos.requests.get")
def test_get_channel_videos_skips_short(mock_get, mock_duration, mock_playlist_id):
    # Mock video duration shorter than MIN_VIDEO_DURATION
    mock_duration.return_value = 10
    mock_playlist_id.return_value = "fake-playlist-id"

    mock_get.return_value.json.return_value = {
        "items": [
            {
                "id": {"videoId": "vid123"},
                "contentDetails": {
                    "videoId": "video123",
                    "videoPublishedAt": "2025-01-01T00:00:00Z"},
                "snippet": {"title": "Too Short", "publishedAt": "2025-01-01T00:00:00Z"}
            }
        ]
    }

    videos = get_channel_videos(channel_id="channel123", api_key="fake_key", max_num_of_videos=1, min_duration=900)
    assert videos == []

@patch("video_to_text.get_yt_videos.get_uploads_playlist_id")
@patch("video_to_text.get_yt_videos.get_video_duration")
@patch("video_to_text.get_yt_videos.requests.get")
def test_get_channel_videos_returns_all_when_min_video_is_none(mock_get, mock_duration, mock_playlist_id):
    # Mock video duration shorter than MIN_VIDEO_DURATION
    mock_duration.return_value = 10
    mock_playlist_id.return_value = "fake-playlist-id"

    mock_get.return_value.json.return_value = {
        "items": [
            {
                "id": {"videoId": "vid123"},
                "contentDetails": {
                    "videoId": "video123",
                    "videoPublishedAt": "2025-01-01T00:00:00Z"},
                "snippet": {"title": "1st Video", "publishedAt": "2025-01-01T00:00:00Z"}
            },
            {
                "id": {"videoId": "vid234"},
                "contentDetails": {
                    "videoId": "video234",
                    "videoPublishedAt": "2025-01-01T00:00:00Z"},
                "snippet": {"title": "2nd Video", "publishedAt": "2025-01-01T00:00:00Z"}
            }

        ]
    }

    videos = get_channel_videos(channel_id="channel123", api_key="fake_key", max_num_of_videos=None, min_duration=0)
    assert len(videos) == 2
    assert videos == [
        {
            'PublishedAt': '2025-01-01T00:00:00Z',
            'Title': '1st Video',
            'URL': 'https://www.youtube.com/watch?v=video123'
        },
        {
            'PublishedAt': '2025-01-01T00:00:00Z',
            'Title': '2nd Video',
            'URL': 'https://www.youtube.com/watch?v=video234'
        }
    ]

@patch("video_to_text.get_yt_videos.get_uploads_playlist_id")
@patch("video_to_text.get_yt_videos.get_video_duration")
@patch("video_to_text.get_yt_videos.requests.get")
def test_get_channel_videos_no_video_present(mock_get, mock_duration, mock_playlist_id):
    # Mock video duration shorter than MIN_VIDEO_DURATION
    mock_duration.return_value = 10
    mock_playlist_id.return_value = "fake-playlist-id"

    mock_get.return_value.json.return_value = {
        "items": []
    }

    videos = get_channel_videos(channel_id="channel123", api_key="fake_key", max_num_of_videos=1, min_duration=900)
    assert videos == []

@patch("video_to_text.get_yt_videos.requests.get")
def test_get_video_duration_success(mock_get):
    mock_get.return_value.json.return_value = {
        "items": [
            {"contentDetails": {"duration": "PT5M"}}
        ]
    }

    duration = get_video_duration("video123", "fake_key")
    assert duration == 300

@patch("video_to_text.get_yt_videos.requests.get")
def test_get_video_duration_invalid(mock_get):
    mock_get.return_value.json.return_value = {
        "items": []
    }

    duration = get_video_duration("video123", "fake_key")
    assert duration == 0
