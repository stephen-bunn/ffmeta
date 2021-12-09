# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains UI presentation callables for the CLI app."""

import contextlib
from functools import partial
from typing import Generator, Iterable, Iterator, List, Optional, Protocol, Tuple

from rich import box
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.table import Column, Table

from ffmeta.types import MediaChapter, TagDefinition
from ffmeta.utils import (
    format_timestamp,
    milliseconds_to_timestamp,
    time_to_milliseconds,
)

from .style import accent_style, danger_style, debug_style, info_style, success_style


def display_panel(console: Console, message: str, title: str, style: str):
    """Display a panel in the terminal.

    Args:
        console (~rich.Console):
            The console instance to use to render the panel
        message (str):
            The message to render in the panel
        title (str):
            The title of the panel
        style (str):
            The general style of the panel
    """

    console.print(Panel.fit(message, title=title, style=style, title_align="left"))


display_error = partial(display_panel, title="Error", style=danger_style)
display_success = partial(display_panel, title="Success", style=success_style)


class StatusProto(Protocol):
    """Defines the protocol we depend on for status."""

    def start(self) -> None:
        """Start the status pending state."""
        ...

    def stop(self) -> None:
        """Stop the status pending state."""
        ...

    def update(self, message: str) -> None:
        """Update the status message.

        Args:
            message (str):
                The new message to use for the status pending state
        """
        ...


@contextlib.contextmanager
def status(console: Console, message: str) -> Generator[StatusProto, None, None]:
    """Enter a status context manager that displays pending state in the console.

    Args:
        console (~rich.console.Console):
            The console to use for rendering the status
        message (str):
            The message to render in the status

    Yields:
        ~StatusProto:
            A status protocol instance
    """

    with console.status(message) as status:
        yield status


def build_header_renderable(title: str, message: str) -> RenderableType:
    """Build a basic header renderable that contains a message.

    Args:
        title (str):
            The title to display before the message
        message (str):
            The message to display within the header

    Returns:
        RenderableType:
            The renderable to display as a header
    """

    return Panel(
        f"[magenta]{title}[/magenta]\n{message}",
        box=box.ROUNDED,
        border_style=accent_style,
    )


def build_tags_renderable(
    tags: Iterable[Tuple[TagDefinition, str]],
    title: Optional[str] = None,
) -> RenderableType:
    """Build a renderable to represent a list of tags.

    Args:
        tags (List[Tuple[TagDefinition, str]]):
            The tags to build a console renderable for
        title (Optional[str]):
            An optional title for the tags to use when necessary
            Defaults to None.

    Returns:
        RenderableType:
            The renderable to use to represent a list of tags
    """

    table = Table(
        Column("Tag", style=debug_style, justify="right", no_wrap=True),
        Column("Value", style=info_style, ratio=3),
        title=title,
        title_justify="left",
        title_style=accent_style,
        box=box.SIMPLE_HEAVY,
        expand=True,
    )

    for definition, value in tags:
        table.add_row(definition.title, value)

    return table


def build_chapter_row(
    chapter: MediaChapter,
    previous_chapter: Optional[MediaChapter] = None,
) -> Tuple[str, str, str, Optional[str]]:
    """Build a single chapter row to place in a table.

    Args:
        chapter (~ffmeta.types.MediaChapter):
            The chapter to build a row for
        previous_chapter (Optional[MediaChapter]):
            The chapter that appears before the chapter we are building a row for.
            Defaults to None.

    Returns:
        Tuple[str, str, str, Optional[str]]:
            A row describing the given chapter
    """

    prev_end = 0
    if previous_chapter is not None:
        prev_end = time_to_milliseconds(previous_chapter.end_time)

    start_ms = time_to_milliseconds(chapter.start_time)
    end_ms = time_to_milliseconds(chapter.end_time)

    has_gap = start_ms != prev_end
    has_overlap = start_ms < prev_end

    issue: Optional[str] = None
    if has_overlap:
        issue = "Chapter overlaps previous"
    elif has_gap:
        issue = "Chapter start does not match previous end"

    return (
        chapter.title,
        (
            f"{format_timestamp(chapter.start_time)} - "
            f"{format_timestamp(chapter.end_time)}"
        ),
        milliseconds_to_timestamp(end_ms - start_ms),
        issue,
    )


def iter_chapter_rows(
    chapters: List[MediaChapter],
    previous_chapter: Optional[MediaChapter] = None,
) -> Iterator[Tuple[str, str, str, Optional[str]]]:
    """Iterate over chapter rows to place in a table.

    Args:
        chapters (List[~ffmeta.types.MediaChapter]):
            The list of chapters to build rows for
        previous_chapter (Optional[~ffmeta.types.MediaChapter]):
            The previous chapter from the given chapters, if required.
            Defaults to None.

    Yields:
        Tuple[str, str, str, Optional[str]]: A row describing a chapter
    """

    for (chapter_index, chapter) in enumerate(chapters):
        yield build_chapter_row(
            chapter,
            previous_chapter=(
                chapters[chapter_index - 1] if chapter_index > 0 else previous_chapter
            ),
        )


def build_chapters_renderable(
    previous_chapters: List[MediaChapter],
    current_chapter: Optional[MediaChapter] = None,
    next_chapters: Optional[List[MediaChapter]] = None,
    title: Optional[str] = None,
) -> RenderableType:
    """Build a renderable to represent a list of chapters.

    Args:
        chapters (List[~.types.MediaChapter]):
            The chapters to build a console renderable for
        next_chapters (Optional[List[~.types.MediaChapter]]):
            The following chapters if you are editing a specific chapter
            Defaults to None.
        title (Optional[str]):
            An optional title for the chapters to use when necessary
            Defaults to None.

    Returns:
        RenderableType:
            The renderable to use to represent a list of chapters
    """

    table = Table(
        Column("Index", style=debug_style, no_wrap=True),
        Column("Title", style=info_style),
        Column("Period", style=debug_style),
        Column("Duration", style=debug_style + Style(italic=True)),
        title=title,
        title_justify="left",
        title_style=accent_style,
        box=box.SIMPLE_HEAVY,
        expand=True,
    )

    has_issues = False
    for (row_index, row) in enumerate(iter_chapter_rows(previous_chapters)):
        if row[-1] is not None:
            has_issues = True

        table.add_row(f"{row_index:02d}", *row)

    if next_chapters:
        table.add_row(*["..."] * 4, end_section=True)
        row_count = len(table.rows)
        for (row_index, row) in enumerate(
            iter_chapter_rows(
                next_chapters,
                previous_chapter=current_chapter,
            )
        ):
            if row[-1] is not None:
                has_issues = True

            table.add_row(f"{row_count + row_index:02d}", *row)

    if has_issues:
        table.add_column("Issue", style=danger_style)

    return table
