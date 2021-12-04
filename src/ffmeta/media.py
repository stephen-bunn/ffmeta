# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains media parsing utilities."""

from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import magic
except ImportError as exc:  # pragma: no cover
    raise ImportError("libmagic binary not found") from exc


class MediaType(Enum):
    """Describes the available types of media."""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"


DEFAULT_BUFFER_SIZE = 2 ** 11


def get_mimetype(
    filepath: Path,
    buffer_size: Optional[int] = None,
) -> Optional[str]:
    """Get a file's guessed mimetype via `libmagic`.

    Args:
        filepath (~pathlib.Path):
            The filepath to guess the mimetype of
        buffer_size (Optional[int]):
            The number of bytes to read in the buffer.
            Defaults to None.

    Raises:
        FileNotFoundError:
            If the given filepath does not exist

    Returns:
        Optional[str]:
            The guessed mimetype
    """

    if not filepath.is_file():
        raise FileNotFoundError(f"No such file {filepath} exists")

    with filepath.open("rb") as buffer:
        return magic.from_buffer(
            buffer.read(buffer_size or DEFAULT_BUFFER_SIZE),
            mime=True,
        )


def get_media_type(
    filepath: Path,
    buffer_size: Optional[int] = None,
) -> Optional[MediaType]:
    """Get a file's guessed media type.

    Args:
        filepath (~pathlib.Path):
            The filepath to guess the media type of
        buffer_size (Optional[int]):
            The number of bytes to read in the buffer.
            Defaults to None.

    Raises:
        FileNotFoundError:
            If the given filepath does not exist

    Returns:
        Optional[MediaType]:
            The guessed media type
    """

    if not filepath.is_file():
        raise FileNotFoundError(f"No such file {filepath} exists")

    mimetype = get_mimetype(filepath, buffer_size=buffer_size)
    if mimetype is None:
        return None

    prefix, *_ = mimetype.split("/")
    try:
        return MediaType(prefix.lower())
    except ValueError:
        return None
