# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains UI presentation callables for the CLI app."""

from functools import partial
from typing import List, Optional, Tuple

from rich import box
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Column, Table
from typer.params import Option


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


display_error = partial(display_panel, title="Error", style="red")
display_success = partial(display_panel, title="Success", style="green")


def build_tags_renderable(
    tags: List[Tuple[str, str]],
    title: Optional[str] = None,
) -> RenderableType:
    """Build a renderable to represent a list of tags.

    Args:
        tags (List[Tuple[str, str]]):
            The tags to build a console renderable for
        title (Optional[str]):
            An optional title for the tags to use when necessary
            Defaults to None.

    Returns:
        RenderableType:
            The renderable to use to represent a list of tags
    """

    table = Table(
        Column("Tag", style="dim", justify="right"),
        Column("Value"),
        title=title,
        title_justify="left",
        box=box.MINIMAL_HEAVY_HEAD,
    )

    for key, value in tags:
        table.add_row(key, value)

    return table
