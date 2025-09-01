import pytest
import os

from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def api_key():
    """
    Retrieves the API key from an environment variable.
    """
    key = os.getenv("YOUTUBE_API_KEY", "DUMMY")
    return key

CASSETTE_DIR = os.path.join(os.path.dirname(__file__), "cassettes")

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "cassette_library_dir": CASSETTE_DIR,
        "record_mode": "once",
        "filter_query_parameters": [("key", "DUMMY")],
        "match_on": ["method", "scheme", "host", "path"]
    }
