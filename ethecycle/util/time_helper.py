"""
Date/time helpers
"""
from datetime import datetime


def current_timestamp_iso8601_str() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()
