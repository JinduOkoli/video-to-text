import pytest
from video_to_text.utils import get_api_key


def test_get_api_key(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test123")
    api_key = get_api_key("YOUTUBE_API_KEY")
    assert api_key == "test123"


def test_get_api_key_missing(monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)

    with pytest.raises(ValueError) as excinfo:
        get_api_key("YOUTUBE_API_KEY")

    assert "API key 'YOUTUBE_API_KEY' not found in environment variables" in str(excinfo.value)
