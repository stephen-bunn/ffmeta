# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains types used throughout the project."""

from dataclasses import dataclass, field
from datetime import time
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from .validators import (
    validate_choice,
    validate_dateformat,
    validate_max_length,
    validate_pattern,
)


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


@dataclass
class TagDefinition:
    """Defines the necessary features of a media tag."""

    title: str
    description: str
    required: bool = field(default=False)
    examples: List[str] = field(default_factory=list)
    validators: Iterable[Callable[[str], None]] = field(default_factory=list)
    read_key: Optional[str] = field(default=None)
    write_key: Optional[str] = field(default=None)


# A suite of tags that are recognized by FFmpeg.
# These are very poorly documented by FFmpeg, so please reference Kodi document instead:
# https://kodi.wiki/view/Video_file_tagging
TAG_DEFINITIONS: Dict[str, TagDefinition] = {
    "album_artist": TagDefinition(
        "Album Artist",
        "Name of the album artist",
    ),
    "album": TagDefinition(
        "Album Title",
        "Name of the album",
    ),
    "sort_album": TagDefinition(
        "Sorting Album Title",
        "Name of the album to use for sorting",
        read_key="sort_album",
        write_key="album-sort",
    ),
    "artist": TagDefinition(
        "Artist Name",
        "Name of the artist",
        read_key="artist",
        write_key="author",
    ),
    "sort_artist": TagDefinition(
        "Sorting Artist Name",
        "Name of the artist to use for sorting",
        read_key="sort_artist",
        write_key="artist-sort",
    ),
    "comment": TagDefinition(
        "Comment",
        "General comments",
    ),
    "compliation": TagDefinition(
        "Compliation",
        "Name of the compliation the content is a part of",
    ),
    "copyright": TagDefinition(
        "Copyright",
        "Copyright information",
        required=True,
    ),
    "creation_time": TagDefinition(
        "Encoded Time",
        "Datetime when the content was encoded",
        required=True,
        validators=[validate_dateformat("%Y-%m-%d %H:%M:%s")],
    ),
    "date": TagDefinition(
        "Release Date",
        "The date the content was released",
        validators=[validate_dateformat("%Y-%m-%d")],
    ),
    "year": TagDefinition(
        "Release Year",
        "The year the content was released",
        validators=[validate_dateformat("%Y")],
    ),
    "encoded_by": TagDefinition(
        "Encoded By",
        "Name of the person or company who encoded the content",
    ),
    "encoder": TagDefinition(
        "Encoder",
        "Name of the software used for encoding",
        required=True,
    ),
    "episode_id": TagDefinition(
        "Episode ID",
        "The unique ID of the episode",
    ),
    "episode_sort": TagDefinition(
        "Episode Number",
        "The episode number within the season",
        validators=[validate_pattern(r"\d+")],
    ),
    "season_number": TagDefinition(
        "Season Number",
        "The season number of a show",
        validators=[validate_pattern(r"\d+")],
    ),
    "genre": TagDefinition(
        "Genre",
        "The genre of the content",
        examples=["Alternative", "Lo-fi", "Punk", "Rock", "Classic Blues"],
    ),
    "grouping": TagDefinition(
        "Grouping",
        "The name of the group this content belongs to",
    ),
    "hd_video": TagDefinition(
        "Video Quality",
        "A flag used to mark the general quality of a video",
        examples=["0 = SD", "1 = 720p", "2 = 1080p/i Full HD", "3 = 2160p UHD"],
        validators=[validate_choice({"0", "1", "2", "3"})],
    ),
    "language": TagDefinition(
        "Language",
        "Language identifier for the original/displayed language (ISO 639-1)",
        required=True,
        examples=["EN", "JA", "ZH"],
        validators=[validate_pattern(r"[A-Z]{2}")],
    ),
    "lyrics": TagDefinition(
        "Lyrics",
        "Unsynchronized lyrics",
    ),
    "media_type": TagDefinition(
        "Media Type",
        "The type of the content",
        examples=["TV Show", "Movie", "Music", "Podcast"],
    ),
    "network": TagDefinition(
        "Network",
        "The name of the network who owns the content",
    ),
    "publisher": TagDefinition(
        "Publisher",
        "The name of a publisher",
    ),
    "producer": TagDefinition(
        "Producer",
        "The name of a producer",
    ),
    "performer": TagDefinition(
        "Performer",
        "The name of a performer",
    ),
    "composer": TagDefinition(
        "Composer",
        "The name of a composer",
    ),
    "director": TagDefinition(
        "Director",
        "The name of a director",
    ),
    "show": TagDefinition(
        "Show",
        "The name of the show the episode belongs to",
    ),
    "synopsis": TagDefinition(
        "Synopsis",
        "Short description of the content",
        validators=[validate_max_length(240)],
    ),
    "description": TagDefinition(
        "Description",
        "Long description of the content",
        required=True,
    ),
    "title": TagDefinition(
        "Title",
        "Title of the content",
        required=True,
    ),
    "sort_name": TagDefinition(
        "Sorting Title",
        "Title of the content to use for sorting",
        read_key="sort_name",
        write_key="title-sort",
    ),
    "subtitle": TagDefinition(
        "Subtitle",
        "Subtitle of the content",
    ),
    "track": TagDefinition(
        "Track",
        "The track identifier for the content",
        examples=["Track Number / Total Tracks"],
        validators=[validate_pattern(r"^\d+\/\d+$")],
    ),
    "disc": TagDefinition(
        "Disc",
        "The disc identifier for the content",
        examples=["Disc Number / Total Discs"],
        validators=[validate_pattern(r"^\d+\/\d+$")],
    ),
    "rating": TagDefinition(
        "Advisory Rating",
        "A flag that is used to mark explicit content",
        required=True,
        examples=["0 = None", "1 = Clean", "2 = Explicit"],
        validators=[validate_choice({"0", "1", "2"})],
    ),
    "location": TagDefinition(
        "Location",
        "GPS coordinates related to the content",
        examples=["+90.0,-127.554334", "45,180", "045,180", "-90.,-180."],
        validators=[
            validate_pattern(r"^((\-?|\+?)?\d+(\.\d+)?),\s*((\-?|\+?)?\d+(\.\d+)?)$"),
        ],
    ),
    "keywords": TagDefinition(
        "Keywords",
        "Generic keywords separated by commas",
    ),
    "URL": TagDefinition(
        "URL",
        "A URL that is related to the content",
    ),
    "podcast": TagDefinition(
        "Podcast Flag",
        "A flag that indicates if some audio content is a podcast",
        examples=["0 = Not Podcast", "1 = Is Podcast"],
        validators=[validate_choice({"0", "1"})],
    ),
    "category": TagDefinition(
        "Podcast Category",
        "The name of the category the podcast belongs to",
    ),
    "episode_uid": TagDefinition(
        "Podcast Episode",
        "The unique ID for the podcast episode",
    ),
}
