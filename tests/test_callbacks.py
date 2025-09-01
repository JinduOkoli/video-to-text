import pytest
import click
from video_to_text.cli.callbacks import parse_max_videos

def test_parse_max_videos_all():
    """When 'all' is passed, should return None (means no limit)."""
    result = parse_max_videos(None, None, "all")
    assert result is None


def test_parse_max_videos_none_uses_default():
    """When None is passed, should use the default of 10."""
    result = parse_max_videos(None, None, None)
    assert result == 10


@pytest.mark.parametrize("value", [0, -1, -10])
def test_parse_max_videos_invalid(value):
    """Values less than 1 should raise click.BadParameter."""
    with pytest.raises(click.BadParameter):
        parse_max_videos(None, None, value)
