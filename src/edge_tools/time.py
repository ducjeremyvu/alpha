import pandas as pd
from typing import List



def convert_index_to_utc(data, time_col='time', tz_from='UTC'):
    """
    Convert a time column to datetime, set it as the index, and ensure the index is in UTC.
    If the index is naive it will be localized to tz_from first, then converted to UTC.
    Returns a copy of the DataFrame with a tz-aware UTC index.
    """
    if time_col not in data.columns:
        raise KeyError(f"{time_col!r} not found in DataFrame")

    df = data.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    df.set_index(time_col, inplace=True)

    # If index is naive, localize to tz_from then convert to UTC; if tz-aware, convert to UTC
    if getattr(df.index, "tz", None) is None:
        df.index = df.index.tz_localize(tz_from).tz_convert('UTC')
    else:
        df.index = df.index.tz_convert('UTC')

    return df


def _add_local_columns(df, tz_to, prefix):
    """
    Helper: given a DataFrame with a tz-aware index (typically UTC), add columns for a target timezone.
    Adds: {prefix}_time, {prefix}_hour, {prefix}_minute, {prefix}_time_only
    Returns a copy of the DataFrame with new columns.
    """
    if getattr(df.index, "tz", None) is None:
        raise ValueError("DataFrame index must be timezone-aware. Call convert_index_to_utc first.")

    out = df.copy()
    out[f'{prefix}_time'] = out.index.tz_convert(tz_to)
    out[f'{prefix}_hour'] = out[f'{prefix}_time'].dt.hour
    out[f'{prefix}_minute'] = out[f'{prefix}_time'].dt.minute
    out[f'{prefix}_time_only'] = out[f'{prefix}_time'].dt.time
    return out


def add_ny_columns(df):
    """Add New York localized time columns (America/New_York)."""
    return _add_local_columns(df, 'America/New_York', 'ny')


def add_tokyo_columns(df):
    """Add Tokyo localized time columns (Asia/Tokyo)."""
    return _add_local_columns(df, 'Asia/Tokyo', 'tokyo')


def add_london_columns(df):
    """Add London localized time columns (Europe/London)."""
    return _add_local_columns(df, 'Europe/London', 'london')


def add_shanghai_columns(df):
    """Add Shanghai localized time columns (Asia/Shanghai)."""
    return _add_local_columns(df, 'Asia/Shanghai', 'shanghai')

def add_hongkong_columns(df):
    """Add Hong Kong localized time columns (Asia/Hong_Kong)."""
    return _add_local_columns(df, 'Asia/Hong_Kong', 'hongkong')

def preprocess_for_premarket_analysis(df, add_tz: List[str] = ['ny', 'tokyo', 'london', 'shanghai', 'hongkong']):
    """
    Full preprocessing: convert index to UTC and add localized time columns for requested timezones.
    
    Args:
        df: Input DataFrame
        add_tz: List of timezone names to add. Valid options: 'ny', 'tokyo', 'london', 'shanghai', 'hongkong'
    
    Returns:
        DataFrame with UTC index and requested timezone columns
    """

    # Mapping of timezone names to their processing functions
    tz_functions = {
        'ny': add_ny_columns,
        'tokyo': add_tokyo_columns,
        'london': add_london_columns,
        'shanghai': add_shanghai_columns,
        'hongkong': add_hongkong_columns
    }
    
    # Validate requested timezones
    invalid_tz = [tz for tz in add_tz if tz not in tz_functions]
    if invalid_tz:
        raise ValueError(f"Invalid timezone(s): {invalid_tz}. Valid options are: {list(tz_functions.keys())}")
    
    # Convert to UTC first
    out = convert_index_to_utc(df)
    
    # Add requested timezone columns
    for tz in add_tz:
        out = tz_functions[tz](out)
    
    return out
