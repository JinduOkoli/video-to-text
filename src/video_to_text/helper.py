from datetime import datetime, timezone
import isodate

def convert_iso_to_datetime(iso_str: str) -> datetime:
    """
    Convert ISO 8601 string to datetime.
    If timezone is provided, assume naive.
    """
    dt = isodate.parse_datetime(iso_str)
    if dt.tzinfo:
        dt = dt.replace(tzinfo=None)
    return dt
