# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains various service calls useful for the project."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Literal, Optional, Tuple, TypedDict, Union
from warnings import warn

import ffmpeg

from ffmeta.ffmetadata import dump_ffmetadata
from ffmeta.utils import milliseconds_to_time

from .types import MediaChapter, MediaMetadata


class StreamDisposition_T(TypedDict):
    """Describes the raw data dictionary for a stream's disposition from `ffprobe`."""

    default: int
    dub: int
    original: int
    comment: int
    lyrics: int
    karaoke: int
    forced: int
    hearing_impaired: int
    visual_impared: int
    clean_effects: int
    attached_pic: int
    timed_thumbnails: int


class BaseStream_T(TypedDict):
    """Base definition of stream data from `ffprobe`.

    Note that this dictionary is only partial.
    Either use `AudioStream_T` or `VideoStream_T` for a full dictionary definition
    of streams from `ffprobe`.
    """

    index: int
    codec_name: str
    codec_long_name: str
    codec_time_base: str
    codec_tag_string: str
    codec_tag: str
    r_frame_rate: str
    avg_frame_rate: str
    time_base: str
    duration_ts: int
    duration: Optional[str]
    disposition: StreamDisposition_T
    tags: Optional[Dict[str, str]]


class AudioStream_T(BaseStream_T):
    """Describes the raw data dictionary describing a audio stream from `ffprobe`."""

    codec_type: Literal["audio"]
    sample_fmt: str
    sample_rate: str
    channels: int
    bits_per_sample: int
    bit_rate: str


class VideoStream_T(BaseStream_T):
    """Describes the raw data dictionary describing a video stream from `ffprobe`."""

    codec_type: Literal["video"]
    width: int
    height: int
    coded_width: int
    coded_height: int
    has_b_frames: int
    pix_fmt: str
    level: int
    color_range: str
    refs: int


class FormatData_T(TypedDict):
    """Describes the raw data dictionary describing media format from `ffprobe`."""

    filename: str
    nb_streams: int
    nb_programs: int
    format_name: str
    format_long_name: str
    duration: str
    size: str
    bit_rate: str
    probe_score: int
    tags: Optional[Dict[str, str]]


class ChapterData_T(TypedDict):
    """Describes the raw data dictionary describing a chapter from `ffprobe`."""

    id: int
    time_base: str
    start: int
    start_time: str
    end: int
    end_time: str
    tags: Optional[Dict[str, str]]


class ProbeData_T(TypedDict):
    """Describes the raw data dictionary returned from `ffprobe`."""

    streams: List[Union[AudioStream_T, VideoStream_T]]
    format: FormatData_T
    chapters: Optional[List[ChapterData_T]]


def probe_media(filepath: Path) -> ProbeData_T:
    """Probe some given media file for the raw data from `ffprobe`.

    Args:
        filepath (~pathlib.Path):
            The media filepath to probe

    Raises:
        FileNotFoundError:
            If the given filepath does not exist

    Returns:
        ProbeData_T:
            The raw data returned from `ffprobe`
    """

    if not filepath.is_file():
        raise FileNotFoundError(f"No such file {filepath} exists")

    return ffmpeg.probe(filepath.as_posix(), **{"show_chapters": None})


def get_audio_stream(probe_data: ProbeData_T) -> Optional[AudioStream_T]:
    """Attempt to extract the first audio stream from some given probe data.

    Args:
        probe_data (ProbeData_T):]
            The probe data to extract the audio stream from

    Returns:
        Optional[AudioStream_T]:]
            The extracted audio stream
    """

    for stream in probe_data["streams"]:
        if stream["codec_type"].lower() == "audio":
            return stream  # type: ignore

    return None


def get_video_stream(probe_data: ProbeData_T) -> Optional[VideoStream_T]:
    """Attempt to extract the first video stream from some given probe data.

    Args:
        probe_data (ProbeData_T):
            The probe data to extract the video from

    Returns:
        Optional[VideoStream_T]:
            The extracted video stream
    """

    for stream in probe_data["streams"]:
        if stream["codec_type"].lower() == "video":
            return stream  # type: ignore

    return None


def probe_metadata(filepath: Path) -> MediaMetadata:
    """Probe a media file for metadata.

    Args:
        filepath (~pathlib.Path):
            The filepath to the media to probe

    Raises:
        FileNotFoundError:
            If the given filepath does not exist
        ValueError:
            If the media could not be probed

    Returns:
        ~types.MediaMetadata:
            The resulting probed metadata
    """

    if not filepath.is_file():
        raise FileNotFoundError(f"No such file {filepath} exists")

    probe = probe_media(filepath)
    media_format = probe.get("format")
    if not media_format:
        raise ValueError(f"No format details discovered from media at {filepath}")

    chapters: List[MediaChapter] = []
    tags: List[Tuple[str, str]] = []

    for key, value in (media_format.get("tags", {}) or {}).items():
        tags.append((key.lower(), value))

    for (chapter_index, chapter) in enumerate(
        sorted(
            (probe.get("chapters", []) or []),
            key=lambda chapter: chapter["start"],
        )
    ):
        chapter_tags = chapter.get("tags", {}) or {}
        chapter_start = chapter.get("start_time")
        chapter_end = chapter.get("end_time")
        if not chapter_start or not chapter_end:
            warn(
                f"Chapter at index {chapter_index} has not start or end times, "
                "skipping chapter"
            )
            continue

        chapters.append(
            MediaChapter(
                title=chapter_tags.get("title", ""),
                description=chapter_tags.get("description"),
                start_time=milliseconds_to_time(int(float(chapter_start) * 1000)),
                end_time=milliseconds_to_time(int(float(chapter_end) * 1000)),
            )
        )

    return MediaMetadata(tags=tags, chapters=chapters)


def write_metadata(
    metadata: MediaMetadata,
    media_filepath: Path,
    output_filepath: Path,
    overwrite: bool = False,
    quiet: bool = True,
) -> Path:
    """Apply some given metadata to some given media content.

    Args:
        metadata (MediaMetadata):
            The metadata to apply
        media_filepath (Path):
            The media to write the metadata to
        output_filepath (Path):
            The output filepath to place the newly created media
        overwrite (bool):
            If true, will allow existing paths to be overwritten
            Defaults to False.
        quiet (bool):
            If true, will silence stdout/stderr output from ffmpeg
            Defaults to True.

    Raises:
        FileNotFoundError:
            If the given media filepath does not exist.
        FileExistsError:
            If the output filepath already exists and overwriting is not allowed.
        ValueError:
            If the output filepath and the media filepath are the same
            In-place overwriting of existing media is not allowed
        IOError:
            If writing out temporary metadata for ffmpeg fails


    Returns:
        ~pathlib.Path:
            The filepath containing the newly created media
            Same as the output filepath
    """

    if not media_filepath.is_file():
        raise FileNotFoundError(f"No such file {media_filepath} exists")

    if not overwrite and output_filepath.exists():
        raise FileExistsError(f"Path {output_filepath} already exists")

    if media_filepath == output_filepath:
        raise ValueError(
            f"Output filepath {output_filepath} cannot be the same as media filepath "
            f"{media_filepath}, no in-place modifications allowed"
        )

    with NamedTemporaryFile("w") as metadata_io:
        dump_ffmetadata(metadata, metadata_io)
        metadata_filepath = Path(metadata_io.name)
        metadata_io.close()

        if not metadata_filepath.is_file():
            raise IOError(
                f"Failed to write temporary metadata out to path {metadata_filepath}"
            )

        command = ffmpeg.input(
            metadata_filepath.as_posix(), **{"i": media_filepath.as_posix()}
        ).output(
            output_filepath.as_posix(),
            **{"map_metadata": 1, "map_chapters": 1, "codec": "copy"},
        )
        command.run(quiet=quiet)

    return output_filepath
