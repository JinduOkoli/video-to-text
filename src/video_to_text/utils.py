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

import click

def parse_max_videos(ctx, param, value):
    """
    Click callback to handle --max-videos option.
    Allows an integer or 'all'.
    Default when not provided: 50.
    """
    if value is None:
        return 50  # default
    if isinstance(value, str) and value.lower() == "all":
        return None  # None means fetch all
    try:
        ivalue = int(value)
        if ivalue < 1:
            raise click.BadParameter("Must be a positive integer or 'all'.")
        return ivalue
    except ValueError:
        raise click.BadParameter("Must be a positive integer or 'all'.")