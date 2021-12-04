# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains serialization methods for various types."""

import dataclasses
import json
from datetime import time
from typing import Any, TextIO

from .types import MediaMetadata
from .utils import format_timestamp, parse_timestamp


def _encoder(obj: Any) -> Any:
    """JSON encoder to handle `datetime.time` instances.

    Args:
        obj (Any):
            The object to encode

    Raises:
        TypeError:
            If the given object type cannot be serialized with JSON

    Returns:
        Any:
            The serialized JSON value
    """

    if isinstance(obj, time):
        return format_timestamp(obj)

    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _decoder(dictionary: dict) -> dict:
    """JSON decoder to handle deserializing chapter times.

    Args:
        dictionary (dict):
            The dictionary to handle decoding

    Returns:
        dict:
            The decoded dictionary
    """

    if "start_time" in dictionary and "end_time" in dictionary:
        dictionary.update(
            dict(
                start_time=parse_timestamp(dictionary["start_time"]),
                end_time=parse_timestamp(dictionary["end_time"]),
            )
        )

    return dictionary


def loads_metadata(content: str) -> MediaMetadata:
    """Load some metadata from a given JSON string.

    Args:
        content (str):
            The JSON string to parse as media metadata

    Returns:
        ~.types.MediaMetadata:
            The loaded metadata
    """

    return json.loads(content, object_hook=_decoder)


def load_metadata(file_handle: TextIO) -> MediaMetadata:
    """Load some dumped metadata from a given file handle.

    Args:
        file_handle (TextIO):
            The file handle to read metadata from

    Returns:
        ~.types.MediaMetadata:
            The loaded metadata
    """

    return loads_metadata(file_handle.read())


def dumps_metadata(metadata: MediaMetadata, **kwargs) -> str:
    """Dump some metadata as a JSON string.

    Args:
        metadata (~.types.MediaMetadata):
            The metadata to encode as JSON

    Returns:
        str:
            The resulting encoded JSON string
    """

    return json.dumps(dataclasses.asdict(metadata), default=_encoder, **kwargs)


def dump_metadata(metadata: MediaMetadata, file_handle: TextIO, **kwargs):
    """Dump some metadata as JSON to a given file handle.

    Args:
        metadata (~.types.MediaMetadata):
            The metadata to write to a file
        file_handle (TextIO):
            The file handle to write the metadata to
    """

    file_handle.write(dumps_metadata(metadata, **kwargs))
