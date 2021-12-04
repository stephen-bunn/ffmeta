# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains utilities to export and import media metadata from the FFMETADATA format."""

import re
from datetime import time
from typing import IO, List, Optional, Tuple

from .types import MediaChapter, MediaMetadata
from .utils import milliseconds_to_time, time_to_milliseconds

FFMETADATA_CHAPTER_PATTERN = re.compile(r"^\[chapter\]$", re.IGNORECASE)
FFMETADATA_KV_PATTERN = re.compile(r"^(?P<key>\w+)=(?P<value>.*)$")


def loads_ffmetadata(content: str) -> MediaMetadata:  # noqa: C901
    """Load some FFMETADATA string as media metadata.

    Args:
        content (str):
            The string to parse as FFMETADATA

    Raises:
        ValueError:
            If the given string does not contain the expected FFMETADTA header
        ValueError:
            If parsing a chapter does not contain all necessary information

    Returns:
        ~.types.MediaMetadata:
            The resulting media metadata
    """

    def _build_media_chapter(
        title: Optional[str],
        description: Optional[str],
        start_time: Optional[time],
        end_time: Optional[time],
    ) -> Optional[MediaChapter]:
        if not title or not start_time or not end_time:
            return None

        return MediaChapter(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
        )

    lines = content.splitlines()
    if lines[0].lower().strip() != ";ffmetadata":
        raise ValueError(
            "Content doesn't appear to be ffmpeg metadata, "
            "must start with ;FFMETADATA header"
        )

    tags: List[Tuple[str, str]] = []
    chapters: List[MediaChapter] = []

    is_parsing_chapter: bool = False
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    title: Optional[str] = None
    description: Optional[str] = None

    for (line_index, line) in enumerate(lines[1:]):
        # skip empty lines
        if len(line.strip()) == 0:
            continue

        if FFMETADATA_CHAPTER_PATTERN.match(line):
            # we are already parsing a chapter, so we've reached the next chapter
            if is_parsing_chapter:
                if not all([title, start_time, end_time]):
                    raise ValueError(
                        f"Parsed chapter before line {line_index} "
                        "appears to be incomplete"
                    )

                if media_chapter := _build_media_chapter(
                    title,
                    description,
                    start_time,
                    end_time,
                ):
                    chapters.append(media_chapter)

                start_time = None
                end_time = None
                title = None
                description = None

            is_parsing_chapter = True
            continue

        kv_match = FFMETADATA_KV_PATTERN.match(line)
        if not kv_match:
            continue

        kv_groups = kv_match.groupdict()
        key = kv_groups["key"].strip()
        value = kv_groups["value"]

        if not is_parsing_chapter:
            # we haven't seen a chapter yet, so we are parsing tags
            tags.append((key, value))
        else:
            key_normalized = key.lower()
            if key_normalized == "start":
                start_time = milliseconds_to_time(int(value))
            elif key_normalized == "end":
                end_time = milliseconds_to_time(int(value))
            elif key_normalized == "title":
                title = value
            elif key_normalized == "description":
                description = value

    if is_parsing_chapter:
        if media_chapter := _build_media_chapter(
            title,
            description,
            start_time,
            end_time,
        ):
            chapters.append(media_chapter)

    return MediaMetadata(tags=tags, chapters=chapters)


def load_ffmetadata(file_handle: IO[str]) -> MediaMetadata:
    """Load some FFMETADATA content from the given file handle.

    Args:
        file_handle (IO[str]):
            The file handle to load FFMETADTA content from

    Returns:
        ~.types.MediaMetadata:
            The loaded media metadata
    """

    return loads_ffmetadata(file_handle.read())


def dumps_ffmetadata_chapter(chapter: MediaChapter) -> str:
    """Dump a media chapter as an FFMETADATA chapter string.

    Args:
        chapter (~.types.MediaChapter):
            The media chapter to dump as a FFMETADATA chapter string

    Returns:
        str:
            The resulting FFMETADATA chapter string
    """

    return "\n".join(
        filter(
            None,
            [
                "[CHAPTER]",
                "TIMEBASE=1/1000",
                f"START={time_to_milliseconds(chapter.start_time)}",
                f"END={time_to_milliseconds(chapter.end_time)}",
                f"title={chapter.title}",
                f"description={chapter.description}" if chapter.description else None,
            ],
        )
    )


def dumps_ffmetadata(metadata: MediaMetadata) -> str:
    """Dump the given metadata as a FFMETADATA string.

    Args:
        metadata (~.types.MediaMetadata):
            The metdata to dump as a FFMETADATA string

    Returns:
        str:
            The resulting FFMETADATA string
    """

    return "\n".join(
        [
            ";FFMETADATA",
            "\n".join(f"{key}={value}" for key, value in metadata.tags),
            "",
            "\n\n".join(
                dumps_ffmetadata_chapter(chapter) for chapter in metadata.chapters
            ),
        ]
    )


def dump_ffmetadata(metadata: MediaMetadata, file_handle: IO[str]):
    """Write the given metadata as FFMETADATA to the provide file handle.

    Args:
        metadata (~.types.MediaMetadata):
            The metadata to write out.
        file_handle (IO[str]):
            The file handle to write the metadata out to.
    """

    file_handle.write(dumps_ffmetadata(metadata))
