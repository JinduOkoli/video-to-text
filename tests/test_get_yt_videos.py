import pytest
from datetime import datetime
from unittest.mock import patch

from video_to_text.exceptions import YouTubeAPIException
from video_to_text.get_yt_videos import (
    get_channel_id,
    get_channel_videos,
    parse_duration,
    get_video_duration,
    get_uploads_playlist_id
)

@pytest.fixture
def fake_videos():
    return {
        "items": [
            {
                "id": {"videoId": "vid123"},
                "contentDetails": {
                    "videoId": "video123",
                    "videoPublishedAt": "2025-01-25T00:00:00Z"},
                "snippet": {"title": "1st Video", "publishedAt": "2025-01-25T00:00:00Z"}
            },
            {
                "id": {"videoId": "vid234"},
                "contentDetails": {
                    "videoId": "video234",
                    "videoPublishedAt": "2025-01-26T00:00:00Z"},
                "snippet": {"title": "2nd Video", "publishedAt": "2025-01-26T00:00:00Z"}
            },
            {
                "id": {"videoId": "vid345"},
                "contentDetails": {
                    "videoId": "video345",
                    "videoPublishedAt": "2025-01-27T00:00:00Z"},
                "snippet": {"title": "3rd Video", "publishedAt": "2025-01-27T00:00:00Z"}
            }
        ]
    }

@pytest.mark.vcr
def test_get_channel_id_success(api_key):
    channel_id = get_channel_id("GoogleDevelopers", api_key)
    assert channel_id == "UC_x5XG1OV2P6uZZ5FSM9Ttw"

@pytest.mark.vcr
def test_get_channel_id_invalid(api_key):
    with pytest.raises(YouTubeAPIException) as excinfo:
        get_channel_id("", api_key)

    assert "Channel not found" in str(excinfo.value)

def test_parse_duration_seconds():
    assert parse_duration("PT1H2M3S") == 3723
    assert parse_duration("PT15M") == 900
    assert parse_duration("PT0S") == 0

@pytest.mark.vcr
def test_get_uploads_playlist_id_success(api_key):
    upload_id = get_uploads_playlist_id("UC_x5XG1OV2P6uZZ5FSM9Ttw", api_key)
    assert upload_id == "UU_x5XG1OV2P6uZZ5FSM9Ttw"

@pytest.mark.vcr
def test_get_uploads_playlist_id_failure(api_key):
    with pytest.raises(YouTubeAPIException) as excinfo:
        get_uploads_playlist_id("Bad_Channel_Id", api_key)

    assert "Could not fetch channel details" in str(excinfo.value)

@pytest.mark.vcr
def test_get_channel_videos_success(api_key):
    channel_id = get_channel_id("GoogleDevelopers", api_key)
    videos = get_channel_videos(channel_id, api_key, max_num_of_videos=2)

    assert isinstance(videos, list)
    assert len(videos) == 2
    assert all("Title" in v for v in videos)
    assert all("URL" in v for v in videos)
    assert all("PublishedAt" in v for v in videos)

@pytest.mark.parametrize(
    "mock_duration_val,min_d,max_d,should_skip",
    [
        (10, 60, None, True),     # too short
        (120, 60, None, False),   # valid, above min
        (500, None, 400, True),   # too long
        (300, None, 400, False),  # valid, under max
        (150, 100, 300, False),   # valid, within both bounds
        (50, 100, 300, True),     # too short, fails min
        (400, 100, 300, True),    # too long, fails max
    ],
)
@patch("video_to_text.get_yt_videos.get_uploads_playlist_id")
@patch("video_to_text.get_yt_videos.get_video_duration")
@patch("video_to_text.get_yt_videos.requests.get")
def test_get_channel_videos_duration_filter(
        mock_get, mock_duration, mock_playlist_id,
        mock_duration_val, min_d, max_d, should_skip
):
    # Arrange
    mock_duration.return_value = mock_duration_val
    mock_playlist_id.return_value = "fake-playlist-id"

    mock_get.return_value.json.return_value = {
        "items": [
            {
                "id": {"videoId": "vid123"},
                "contentDetails": {
                    "videoId": "video123",
                    "videoPublishedAt": "2025-01-01T00:00:00Z"},
                "snippet": {
                    "title": "Sample Video",
                    "publishedAt": "2025-01-01T00:00:00Z"
                }
            }
        ]
    }

    # Act
    videos = get_channel_videos(
        channel_id="fake-channel",
        api_key="fake_key",
        max_num_of_videos=1,
        min_duration=min_d,
        max_duration=max_d
    )

    # Assert
    if should_skip:
        assert videos == []
    else:
        assert len(videos) == 1
        assert videos[0]["Title"] == "Sample Video"

@patch("video_to_text.get_yt_videos.get_uploads_playlist_id")
@patch("video_to_text.get_yt_videos.get_video_duration")
@patch("video_to_text.get_yt_videos.requests.get")
def test_get_channel_videos_returns_all_when_min_video_is_none(mock_get, mock_duration, mock_playlist_id, fake_videos):
    # Mock video duration shorter than MIN_VIDEO_DURATION
    mock_duration.return_value = 10
    mock_playlist_id.return_value = "fake-playlist-id"

    mock_get.return_value.json.return_value = fake_videos

    videos = get_channel_videos(channel_id="channel123", api_key="fake_key", max_num_of_videos=None)
    assert len(videos) == 3
    assert videos == [
        {
            'PublishedAt': '2025-01-25T00:00:00Z',
            'Title': '1st Video',
            'URL': 'https://www.youtube.com/watch?v=video123'
        },
        {
            'PublishedAt': '2025-01-26T00:00:00Z',
            'Title': '2nd Video',
            'URL': 'https://www.youtube.com/watch?v=video234'
        },
        {
            'PublishedAt': '2025-01-27T00:00:00Z',
            'Title': '3rd Video',
            'URL': 'https://www.youtube.com/watch?v=video345'
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

    videos = get_channel_videos(channel_id="channel123", api_key="fake_key", max_num_of_videos=1)
    assert videos == []

@pytest.mark.parametrize(
    "start_date, end_date, expected_titles",
    [
        (
                datetime(2025, 1, 25),
                datetime(2025, 1, 27),
                ["1st Video", "2nd Video", "3rd Video"],
        ),
        (
                datetime(2025, 1, 26),
                None,
                ["2nd Video", "3rd Video"],
        ),
        (
                None,
                datetime(2025, 1, 25, 23, 59, 59),
                ["1st Video"],
        ),
        (
                datetime(2025, 1, 28),
                None,
                [],
        ),
    ],
)
@patch("video_to_text.get_yt_videos.get_uploads_playlist_id")
@patch("video_to_text.get_yt_videos.get_video_duration")
@patch("video_to_text.get_yt_videos.requests.get")
def test_get_channel_videos_date_range(mock_get, mock_duration, mock_playlist_id, fake_videos,
                                       start_date, end_date, expected_titles):
    mock_duration.return_value = 10
    mock_playlist_id.return_value = "fake-playlist-id"

    mock_get.return_value.json.return_value = fake_videos

    videos = get_channel_videos(channel_id="channel123",
                                api_key="fake_key",
                                max_num_of_videos=None,
                                start_date=start_date,
                                end_date=end_date)
    titles = [v["Title"] for v in videos]
    assert sorted(titles) == sorted(expected_titles)

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
