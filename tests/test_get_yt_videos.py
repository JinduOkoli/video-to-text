import pytest
from video_to_text.get_yt_videos import get_channel_id, get_channel_videos

API_KEY = "TEST-API-KEY"

@pytest.mark.vcr
def test_get_channel_id():
    channel_id = get_channel_id("GoogleDevelopers", API_KEY)
    assert channel_id == "UC_x5XG1OV2P6uZZ5FSM9Ttw"

@pytest.mark.vcr
def test_get_channel_id_invalid():
    with pytest.raises(ValueError) as excinfo:
        get_channel_id("", API_KEY)

    assert "Channel not found" in str(excinfo.value)

