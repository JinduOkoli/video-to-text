import pytest
from datetime import datetime

from video_to_text.helper import convert_iso_to_datetime

@pytest.mark.parametrize(
    "iso_date, expected_results",
    [
        (
                "2025-04-15T21:21:33Z",
                datetime(2025, 4, 15, 21, 21, 33)
        ),
        (
                "2025-01-01T12:12:20+0000",
                datetime(2025, 1, 1, 12, 12, 20)
        )
    ]
)
def test_convert_iso_to_datetime(iso_date, expected_results):
    result = convert_iso_to_datetime(iso_date)

    assert isinstance(result, datetime)
    assert not result.tzinfo
    assert result == expected_results
