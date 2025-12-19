from datetime import datetime, timezone
from typing import Optional
import zoneinfo  # Available in Python 3.9+, use backports.zoneinfo for earlier versions


def get_utc_now() -> datetime:
    """Get current time in UTC timezone-aware datetime."""
    return datetime.now(timezone.utc)


def get_timezone_aware_datetime(dt: datetime, tz_name: str = "UTC") -> datetime:
    """Convert a naive datetime to a timezone-aware datetime."""
    if dt.tzinfo is not None:
        # Already timezone-aware
        return dt
    # Make it timezone-aware by assuming it's in the specified timezone
    tz = zoneinfo.ZoneInfo(tz_name)
    return dt.replace(tzinfo=tz)


def convert_to_timezone(dt: datetime, tz_name: str) -> datetime:
    """Convert a datetime to a different timezone."""
    if dt.tzinfo is None:
        # Assume it's UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    target_tz = zoneinfo.ZoneInfo(tz_name)
    return dt.astimezone(target_tz)


def format_datetime_for_display(dt: datetime, tz_name: str = "UTC", 
                               fmt: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """Format a datetime object for display with timezone information."""
    if dt.tzinfo is None:
        # Make timezone-aware if needed
        dt = dt.replace(tzinfo=timezone.utc)
    
    target_tz = zoneinfo.ZoneInfo(tz_name)
    converted_dt = dt.astimezone(target_tz)
    return converted_dt.strftime(fmt)


def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO format with timezone info."""
    if dt and dt.tzinfo is None:
        # Make timezone-aware by assuming UTC if not already set
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat() if dt else None