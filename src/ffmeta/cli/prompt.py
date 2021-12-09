# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains various user prompts that are used throughout the CLI apps."""

import contextlib
from datetime import time
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.prompt import Confirm, Prompt, PromptBase

from ffmeta.types import MediaChapter, MediaMetadata, TagDefinition, iter_desired_tags
from ffmeta.utils import format_timestamp, parse_timestamp, timestamp_to_milliseconds

from .style import danger_style
from .ui import (
    build_chapters_renderable,
    build_header_renderable,
    build_tags_renderable,
)


def prompt_confirm(console: Console, message: str, default: bool = True) -> bool:
    """Prompt the user for a simple boolean confirmation.

    Note that this confirmation dialog defaults to be `True`.

    Args:
        console (~rich.console.Console):
            The console instance to use for rendering
        message (str):
            The message to prompt the user with
        default (bool):
            The default boolean state of the confirm.
            Defaults to True.

    Returns:
        bool: True if the user confirmed
    """

    return Confirm.ask(message, console=console, default=default)


def prompt_value(
    console: Console,
    message: str,
    default: Optional[str] = None,
    hidden: bool = False,
    empty_allowed: bool = False,
    trailing_whitespace_allowed: bool = False,
    prompt_type: PromptBase[str] = Prompt,  # type: ignore
) -> str:
    """Prompt the user for a string value.

    Args:
        console (rich.console.Console):
            The console to display the prompt with
        message (str):
            The message to prompt the user with
        default (Optional[str]):
            The optional default value of the prompt.
            Defaults to None.
        hidden (bool):
            If true, hides user input.
            Defaults to False.
        empty_allowed (bool):
            Allows empty input from the user.
            Defaults to False.
        trailing_whitespace_allowed (bool):
            If true, will not trim trailing whitespace from the input.
            Defaults to False.
        prompt_type (PromptBase[str]):
            The type of prompt to prompt the user with.
            Defaults to Prompt.

    Returns:
        str:
            The user given value
    """

    value = ""
    while len(value) <= 0:
        value = (
            prompt_type.ask(
                message,
                console=console,
                password=hidden,
                default=default or "",
                show_default=default is not None,
            )
            or ""
        )

        if len(value) == 0:
            if empty_allowed:
                break

            console.print(f"Please provide a value for {message!r}", style=danger_style)

    if trailing_whitespace_allowed:
        return value

    return value.strip()


def prompt_tag(
    console: Console,
    tag_definition: TagDefinition,
    default: Optional[str] = None,
) -> str:
    """Prompt the user to provide a tag value given a tag definition.

    Args:
        console (~rich.console.Console):
            The console to use for rendering
        tag_definition (~ffmeta.types.TagDefinition):
            The tag definition to prompt the user for
        default (Optional[str]):
            The default value to use for the prompt.
            Defaults to None.

    Returns:
        str:
            The user provided tag value
    """

    console.print(
        f"[dim]{tag_definition.description}[/dim]"
        + (
            f" ({', '.join(tag_definition.examples)})"
            if tag_definition.examples
            else ""
        )
    )

    while True:
        is_valid = True
        tag_default = (
            default
            if default
            else (tag_definition.default() if tag_definition.default else None)
        )
        tag_value = prompt_value(console, tag_definition.title, default=tag_default)
        for validator in tag_definition.validators:
            try:
                validator(tag_value)
            except ValueError as exc:
                is_valid = False
                console.print(f"{exc}", style=danger_style)

        if not is_valid:
            continue

        return tag_value


def prompt_time(
    console: Console,
    message: str,
    default: Optional[str] = None,
) -> time:
    """Prompt the user for a specific timestamp.

    Args:
        console (~rich.console.Console):
            The console instance to use for rendering
        message (str):
            The message to display to the user
        default (Optional[str], optional):
            The default value to use for the prompt.
            Defaults to None.

    Returns:
        datetime.time:
            The time the user provided
    """

    while True:
        value = prompt_value(console, message, default=default)
        try:
            timestamp_to_milliseconds(value)
            return parse_timestamp(value)
        except ValueError:
            console.print(f"{value} is not a valid timestamp", style=danger_style)


def prompt_media_tags(
    console: Console,
    media_filepath: Path,
    metadata: MediaMetadata,
) -> List[Tuple[TagDefinition, str]]:
    """Prompt the user to provide desired tags for some given media.

    Args:
        console (~rich.console.Console):
            The console instance to use for rendering
        media_filepath (~pathlib.Path):
            The filepath to the media we are prompting tags for
        metadata (~ffmeta.types.MediaMetadata):
            The loaded metadata from the given media

    Returns:
        List[Tuple[TagDefinition, str]]:
            Many tuples containing the tag definition and user-provided tag value
    """

    tags: List[Tuple[TagDefinition, str]] = []

    for definition in iter_desired_tags(media_filepath):
        console.clear()
        console.print(build_header_renderable(f"{media_filepath.name} Tags"))
        console.print(build_tags_renderable(tags))

        default: Optional[str] = None
        with contextlib.suppress(StopIteration):
            default = next(metadata.find_tags(definition))

        value = prompt_tag(console, definition, default=default)
        tags.append((definition, value))

    return tags


def prompt_media_chapter(
    console: Console,
    media_filepath: Path,
    current_chapter: Optional[MediaChapter] = None,
    previous_chapters: Optional[List[MediaChapter]] = None,
    next_chapters: Optional[List[MediaChapter]] = None,
) -> MediaChapter:
    """Prompt the user to provide chapter information.

    Args:
        console (~rich.console.Console):
            The console instance to use for rendering
        media_filepath (~pathlib.Path):
            The filepath to the media we are building chapters for
        current_chapter (Optional[~ffmeta.types.MediaChapter]):
            The current chapter we are editing (if available).
            Defaults to None.
        previous_chapters (Optional[List[~ffmeta.types.MediaChapter]]):
            The chapters that appear prior to the current chapter (if available).
            Defaults to None.
        next_chapters (Optional[List[~ffmeta.types.MediaChapter]]):
            The chapters that appear after the current chapter (if available).
            Defaults to None.

    Returns:
        ~ffmeta.types.MediaChapter:
            The chapter instance that the user provided information for
    """

    console.clear()
    console.print(build_header_renderable(f"{media_filepath.name} Chapters"))
    console.print(
        build_chapters_renderable(
            previous_chapters or [],
            current_chapter=current_chapter,
            next_chapters=next_chapters,
        )
    )

    title = prompt_value(
        console,
        "Chapter Title",
        default=current_chapter.title if current_chapter else None,
    )

    previous_chapter = (
        previous_chapters[-1]
        if previous_chapters and len(previous_chapters) > 0
        else None
    )
    start_default = (
        current_chapter.start_time
        if current_chapter
        else (previous_chapter.end_time if previous_chapter else None)
    )
    start_time = prompt_time(
        console,
        "Chapter Start",
        default=format_timestamp(start_default) if start_default else None,
    )

    end_default = current_chapter.end_time if current_chapter else None
    end_time = prompt_time(
        console,
        "Chapter End",
        default=format_timestamp(end_default) if end_default else None,
    )

    return MediaChapter(title=title, start_time=start_time, end_time=end_time)


def prompt_media_chapters(
    console: Console,
    media_filepath: Path,
    metadata: MediaMetadata,
) -> List[MediaChapter]:
    """Prompt the use to provide information for many chapters.

    Args:
        console (~rich.console.Console):
            The console to use for rendering
        media_filepath (~pathlib.Path):
            The filepath to the media we are editing the chapters of
        metadata (~ffmeta.types.MediaMetadata):
            The parsed metadata for the given media

    Returns:
        List[~ffmeta.types.MediaChapter]:
            An ordered list of chapters instances the user populated
    """

    chapters: List[MediaChapter] = []

    if len(metadata.chapters) > 0:
        # prompt editing of existing chapters
        for (metadata_chapter_index, metadata_chapter) in enumerate(metadata.chapters):
            chapter = prompt_media_chapter(
                console,
                media_filepath,
                current_chapter=metadata_chapter,
                previous_chapters=chapters,
                next_chapters=metadata.chapters[metadata_chapter_index + 1 :],
            )
            chapters.append(chapter)

            if not prompt_confirm(console, "\nContinue?"):
                return chapters

    # prompt editing of new chapters
    while True:
        chapter = prompt_media_chapter(
            console,
            media_filepath,
            current_chapter=None,
            previous_chapters=chapters,
        )
        chapters.append(chapter)
        if not prompt_confirm(console, "\nContinue?"):
            return chapters
