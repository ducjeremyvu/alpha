from datetime import datetime, date
from dateutil import parser

def to_datetime(x, *, assume_tz="UTC", ms_threshold=1e11):
    """
    Convert common date-like inputs to a datetime.datetime object.
    
    Parameters
    ----------
    x : Any
        Input to convert. Can be:
        - datetime.datetime
        - datetime.date
        - int/float timestamp (seconds or milliseconds)
        - str date
    assume_tz : str, optional
        Timezone to assign when none is present.
    ms_threshold : int/float, optional
        If numeric is > this value, treat as milliseconds instead of seconds.

    Returns
    -------
    datetime.datetime
    """
    
    # Already a datetime
    if isinstance(x, datetime):
        return x
    
    # A plain date → make datetime at midnight
    if isinstance(x, date):
        return datetime(x.year, x.month, x.day)
    
    # Numeric timestamp
    if isinstance(x, (int, float)):
        # If it's huge → likely ms
        if x > ms_threshold:
            x /= 1000.0
        return datetime.fromtimestamp(x)
    
    # Strings → let dateutil handle the mess
    if isinstance(x, str):
        dt = parser.parse(x)
        # If string had no timezone, apply assume_tz
        if dt.tzinfo is None and assume_tz:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(assume_tz))
        return dt
    
    raise TypeError(f"Don't know how to convert type {type(x)} to datetime")


