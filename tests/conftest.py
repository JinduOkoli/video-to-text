import pytest
import os


CASSETTE_DIR = os.path.join(os.path.dirname(__file__), "cassettes")

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "cassette_library_dir": CASSETTE_DIR,
        "record_mode": "once",
        "filter_query_parameters": [("key", "DUMMY")],
        "match_on": ["method", "scheme", "host", "path"]
    }
