"""
datetime_utils.py

Common datetime helper functions.
"""

from datetime import datetime


# ---------------------------------------------------------
# Current Timestamp
# ---------------------------------------------------------

def current_timestamp():
    """
    Returns current timestamp in ISO format.

    Example:
    2026-07-20T10:45:23
    """

    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------
# Parse Timestamp
# ---------------------------------------------------------

def parse_timestamp(timestamp):
    """
    Converts ISO timestamp string into datetime object.
    """

    return datetime.fromisoformat(timestamp)


# ---------------------------------------------------------
# Age In Days
# ---------------------------------------------------------

def age_in_days(timestamp):
    """
    Returns age in days from the given timestamp.
    """

    timestamp = parse_timestamp(timestamp)

    return (datetime.now() - timestamp).days