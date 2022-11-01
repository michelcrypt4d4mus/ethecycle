"""
Date/time helpers
"""
from datetime import datetime

EXTRACTED_AT = 'extracted_at'


def current_timestamp_iso8601_str() -> str:
    datetime.utcnow().replace(microsecond=0).isoformat()
