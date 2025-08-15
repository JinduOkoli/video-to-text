import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(key_name) -> str:
    """
    Retrieve API KEY from env

    :param key_name: API key name
    :return: API key
    """
    api_key = os.getenv(key_name)

    if api_key is None:
        raise ValueError(f"API key '{key_name}' not found in environment variables.")
    return api_key
