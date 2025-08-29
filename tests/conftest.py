import os
import pytest
import vcr

# Load environment variables from .env for local development
from dotenv import load_dotenv
load_dotenv()

# Get API key from environment (works in CI too)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Ensure API key exists locally or in CI
if not YOUTUBE_API_KEY:
    pytest.skip("YOUTUBE_API_KEY not set. Skipping tests that require it.", allow_module_level=True)

# Absolute path to cassettes directory
CASSETTE_DIR = os.path.join(os.path.dirname(__file__), "cassettes")

# VCR configuration
my_vcr = vcr.VCR(
    cassette_library_dir=CASSETTE_DIR,
    record_mode="once",  # record only if cassette missing
    match_on=["method", "scheme", "host", "path", "query"],
    filter_query_parameters=[("key", YOUTUBE_API_KEY)],  # hide API key
    filter_headers=["authorization"],  # hide auth headers if used
)
