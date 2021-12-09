# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains types used throughout the project."""

import os
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple

from ffmeta.media import MediaType, get_media_type

from .validators import (
    validate_choice,
    validate_dateformat,
    validate_max_length,
    validate_pattern,
)


@dataclass
class TagDefinition:
    """Defines the necessary features of a media tag."""

    title: str
    description: str
    key: str
    examples: List[str] = field(default_factory=list)
    validators: Iterable[Callable[[str], None]] = field(default_factory=list)
    write_key: Optional[str] = field(default=None)
    default: Optional[Callable[..., Optional[str]]] = field(default=None)


# A suite of tags that are recognized by FFmpeg.
# These are very poorly documented by FFmpeg, so please reference Kodi document instead:
# https://kodi.wiki/view/Video_file_tagging
TAG_DEFINITIONS: Dict[str, TagDefinition] = {
    "album_artist": TagDefinition(
        "Album Artist",
        "Name of the album artist",
        "album_artist",
    ),
    "album": TagDefinition(
        "Album Title",
        "Name of the album",
        "album",
    ),
    "sort_album": TagDefinition(
        "Sorting Album Title",
        "Name of the album to use for sorting",
        "sort_album",
        write_key="album-sort",
    ),
    "artist": TagDefinition(
        "Artist Name",
        "Name of the artist",
        "artist",
        write_key="author",
    ),
    "sort_artist": TagDefinition(
        "Sorting Artist Name",
        "Name of the artist to use for sorting",
        "sort_artist",
        write_key="artist-sort",
    ),
    "comment": TagDefinition(
        "Comment",
        "General comments",
        "comment",
    ),
    "compliation": TagDefinition(
        "Compliation",
        "Name of the compliation the content is a part of",
        "compliation",
    ),
    "copyright": TagDefinition(
        "Copyright",
        "Copyright information",
        "copyright",
    ),
    "creation_time": TagDefinition(
        "Encoded Time",
        "Datetime when the content was encoded",
        "creation_time",
        validators=[validate_dateformat("%Y-%m-%dT%H:%M:%S.%fZ")],
        default=lambda: f"{datetime.now().isoformat()}Z",
    ),
    "date": TagDefinition(
        "Release Date",
        "The date the content was released",
        "date",
        validators=[validate_dateformat("%Y-%m-%d")],
    ),
    "year": TagDefinition(
        "Release Year",
        "The year the content was released",
        "year",
        validators=[validate_dateformat("%Y")],
    ),
    "encoded_by": TagDefinition(
        "Encoded By",
        "Name of the person or company who encoded the content",
        "encoded_by",
        default=lambda: os.getenv("FFMETA_ENCODED_BY"),
    ),
    "encoder": TagDefinition(
        "Encoder",
        "Name of the software used for encoding",
        "encoder",
    ),
    "episode_id": TagDefinition(
        "Episode ID", "The unique ID of the episode", "episode_id"
    ),
    "episode_sort": TagDefinition(
        "Episode Number",
        "The episode number within the season",
        "episode_sort",
        validators=[validate_pattern(r"^\d+$")],
    ),
    "season_number": TagDefinition(
        "Season Number",
        "The season number of a show",
        "season_number",
        validators=[validate_pattern(r"^\d+$")],
    ),
    "genre": TagDefinition(
        "Genre",
        "The genre of the content",
        "genre",
        examples=["Alternative", "Lo-fi", "Punk", "Rock", "Classic Blues"],
    ),
    "grouping": TagDefinition(
        "Grouping",
        "grouping",
        "The name of the group this content belongs to",
    ),
    "hd_video": TagDefinition(
        "Video Quality",
        "A flag used to mark the general quality of a video",
        "hd_video",
        examples=["0 = SD", "1 = 720p", "2 = 1080p/i Full HD", "3 = 2160p UHD"],
        validators=[validate_choice({"0", "1", "2", "3"})],
    ),
    "language": TagDefinition(
        "Language",
        "Language identifier for the original/displayed language (ISO 639-1)",
        "language",
        examples=["EN", "JA", "ZH"],
        validators=[validate_pattern(r"^[A-Z]{2}$")],
    ),
    "lyrics": TagDefinition(
        "Lyrics",
        "Unsynchronized lyrics",
        "lyrics",
    ),
    "media_type": TagDefinition(
        "Media Type",
        "The type of the content",
        "media_type",
        examples=["TV Show", "Movie", "Music", "Podcast"],
    ),
    "network": TagDefinition(
        "Network",
        "The name of the network who owns the content",
        "network",
    ),
    "publisher": TagDefinition(
        "Publisher",
        "The name of a publisher",
        "publisher",
    ),
    "producer": TagDefinition(
        "Producer",
        "The name of a producer",
        "producer",
    ),
    "performer": TagDefinition(
        "Performer",
        "The name of a performer",
        "performer",
    ),
    "composer": TagDefinition(
        "Composer",
        "The name of a composer",
        "composer",
    ),
    "director": TagDefinition(
        "Director",
        "The name of a director",
        "director",
    ),
    "show": TagDefinition(
        "Show",
        "The name of the show the episode belongs to",
        "show",
    ),
    "synopsis": TagDefinition(
        "Synopsis",
        "Short description of the content",
        "synopsis",
        validators=[validate_max_length(240)],
    ),
    "description": TagDefinition(
        "Description",
        "Long description of the content",
        "description",
    ),
    "title": TagDefinition(
        "Title",
        "Title of the content",
        "title",
    ),
    "sort_name": TagDefinition(
        "Sorting Title",
        "Title of the content to use for sorting",
        "sort_name",
        write_key="title-sort",
    ),
    "subtitle": TagDefinition(
        "Subtitle",
        "Subtitle of the content",
        "subtitle",
    ),
    "track": TagDefinition(
        "Track",
        "The track identifier for the content",
        "track",
        examples=["Track Number / Total Tracks"],
        validators=[validate_pattern(r"^\d+\/\d+$")],
    ),
    "disc": TagDefinition(
        "Disc",
        "The disc identifier for the content",
        "disc",
        examples=["Disc Number / Total Discs"],
        validators=[validate_pattern(r"^\d+\/\d+$")],
    ),
    "rating": TagDefinition(
        "Advisory Rating",
        "A flag that is used to mark explicit content",
        "rating",
        examples=["0 = None", "1 = Clean", "2 = Explicit"],
        validators=[validate_choice({"0", "1", "2"})],
        default=lambda: "1",
    ),
    "location": TagDefinition(
        "Location",
        "GPS coordinates related to the content",
        "location",
        examples=["+90.0,-127.554334", "45,180", "045,180", "-90.,-180."],
        validators=[
            validate_pattern(r"^((\-?|\+?)?\d+(\.\d+)?),\s*((\-?|\+?)?\d+(\.\d+)?)$"),
        ],
    ),
    "keywords": TagDefinition(
        "Keywords",
        "Generic keywords separated by commas",
        "keywords",
    ),
    "URL": TagDefinition(
        "URL",
        "A URL that is related to the content",
        "URL",
    ),
    "podcast": TagDefinition(
        "Podcast Flag",
        "A flag that indicates if some audio content is a podcast",
        "podcast",
        examples=["0 = Not Podcast", "1 = Is Podcast"],
        validators=[validate_choice({"0", "1"})],
    ),
    "category": TagDefinition(
        "Podcast Category",
        "The name of the category the podcast belongs to",
        "category",
    ),
    "episode_uid": TagDefinition(
        "Podcast Episode",
        "The unique ID for the podcast episode",
        "episode_uid",
    ),
}


REQUIRED_TAG_DEFINITIONS: List[TagDefinition] = [
    TAG_DEFINITIONS["title"],
    TAG_DEFINITIONS["description"],
    TAG_DEFINITIONS["language"],
    TAG_DEFINITIONS["encoder"],
    TAG_DEFINITIONS["encoded_by"],
    TAG_DEFINITIONS["creation_time"],
    TAG_DEFINITIONS["rating"],
    TAG_DEFINITIONS["copyright"],
]

DESIRED_TAG_DEFINITIONS: Dict[MediaType, List[TagDefinition]] = {
    MediaType.VIDEO: [
        TAG_DEFINITIONS["hd_video"],
    ],
    MediaType.AUDIO: [
        TAG_DEFINITIONS["genre"],
        TAG_DEFINITIONS["track"],
        TAG_DEFINITIONS["disc"],
    ],
}


def iter_desired_tags(media_filepath: Path) -> Iterator[TagDefinition]:
    """Iterate over the desired tag keys and definitions for some media.

    Args:
        media_filepath (pathlib.Path):
            The path the the media that needs to be tagged

    Yields:
        TagDefinition:
            A tag definition instance
    """

    for definition in REQUIRED_TAG_DEFINITIONS:
        yield definition

    media_type = get_media_type(media_filepath)
    if not media_type:
        return

    for definition in DESIRED_TAG_DEFINITIONS.get(media_type, []):
        yield definition


@dataclass
class MediaChapter:
    """Describes a media chapter."""

    title: str = field()
    start_time: time = field()
    end_time: time = field()
    description: Optional[str] = field(default=None)


@dataclass
class MediaMetadata:
    """Describes basic media metadata."""

    version: str = field(default="1")
    tags: List[Tuple[str, str]] = field(default_factory=list)
    chapters: List[MediaChapter] = field(default_factory=list)

    def find_tags(self, tag_definition: TagDefinition) -> Iterator[str]:
        """Find any tags using the given definition from the metadata.

        Args:
            tag_definition (~TagDefinition):
                The definition to find the tag value for

        Yields:
            str:
                A discoverd tag value matching the given tag definition
        """

        for key, value in self.tags:
            if key.lower() == tag_definition.key.lower():
                yield value

    def iter_defined_tags(self) -> Iterator[Tuple[TagDefinition, str]]:
        """Iterate over all known tags that have definitions from the metadata.

        Yields:
            Tuple[~TagDefinition, str]:
                A tuple of the tag definition and tag value
        """

        for tag_key, tag_value in self.tags:
            if tag_key not in TAG_DEFINITIONS:
                continue

            yield (TAG_DEFINITIONS[tag_key], tag_value)
