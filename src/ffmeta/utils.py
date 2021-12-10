# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains generic utilities that are useful throughout the project."""

import re
from datetime import datetime, time

TIMESTAMP_PATTERN = re.compile(
    r"(?:(?P<hours>\d+):)?"
    r"(?P<minutes>\d{1,2}):(?P<seconds>\d{1,2})"
    r"(?:\.(?P<milliseconds>\d{0,3}))?"
)


def noop(*args, **kwargs) -> None:
    """Noop function that does absolutely nothing."""

    return None


def timestamp_to_time(timestamp: str) -> time:
    """Build a time instance from a user provided timestamp.

    Args:
        timestamp (str):
            The user provided timestamp

    Raises:
        ValueError:
            If the given timestamp string does not match the expected pattern

    Returns:
        time:
            The produced time instance
    """

    match = TIMESTAMP_PATTERN.match(timestamp)
    if not match:
        raise ValueError(f"timestamp {timestamp} is not a valid timestamp")

    groups = match.groupdict()
    return time(
        hour=int(groups.get("hours", 0) or 0),
        minute=int(groups.get("minutes", 0)),
        second=int(groups.get("seconds", 0)),
        microsecond=int(groups.get("milliseconds", 0) or 0) * 1000,
    )


def parse_timestamp(timestamp: str) -> time:
    """Parse a formatted timestamp as a time instance.

    Args:
        timestamp (str):
            The formatted timestamp to parse

    Returns:
        time:
            The parsed time
    """

    return datetime.strptime(f"{timestamp}000", "%H:%M:%S.%f").time()


def format_timestamp(timestamp: time) -> str:
    """Format a given time in the appropriate timestamp format.

    Args:
        timestamp (datetime.time):
            The timestamp to format

    Returns:
        str:
            The formatted timestamp
    """

    # %f is microseconds, remove trailing 3 spaces
    return timestamp.strftime("%H:%M:%S.%f")[:-3]


def milliseconds_to_time(milliseconds: int) -> time:
    """Get the equivalent time for the given milliseconds value.

    Args:
        milliseconds (int):
            The number of milliseconds to cast as a time.

    Returns:
        datetime.time:
            The time representing the provided milliseconds.
    """

    return (
        datetime.utcfromtimestamp(milliseconds // 1000)
        .replace(microsecond=milliseconds % 1000 * 1000)
        .time()
    )


def milliseconds_to_timestamp(milliseconds: int) -> str:
    """Get the equivalent timestamp for the given millseconds value.

    Args:
        milliseconds (int):
            The number of milliseconds to display as as timestamp.

    Returns:
        str:
            The formatted timestamp for the given milliseconds.
    """

    return format_timestamp(milliseconds_to_time(milliseconds))


def timestamp_to_milliseconds(timestamp: str) -> int:
    """Get the equivalent milliseconds from the given timestamp.

    Args:
        timestamp (str):
            A timestamp in format "HH:MM:SS.fff".

    Raises:
        ValueError:
            When the given timestamp doesn't match the expected pattern.

    Returns:
        int:
            The amount of time in milliseconds.
    """

    match = TIMESTAMP_PATTERN.match(timestamp)
    if not match:
        raise ValueError(f"{timestamp!r} is not a valid timestamp")

    groups = match.groupdict()
    hours = int(groups.get("hours", 0) or 0)
    minutes = int(groups.get("minutes", 0))
    seconds = int(groups.get("seconds", 0))
    milliseconds = int(groups.get("milliseconds", 0) or 0)

    return (((((hours * 60) + minutes) * 60) + seconds) * 1000) + milliseconds


def time_to_milliseconds(timestamp: time) -> int:
    """Get the equivalent milliseconds from the given time.

    Args:
        timestamp (datetime.time):
            The time to get as milliseconds.

    Returns:
        int:
            The amount of time in milliseconds.
    """

    return timestamp_to_milliseconds(format_timestamp(timestamp))
