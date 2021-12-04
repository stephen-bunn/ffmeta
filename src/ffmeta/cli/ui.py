# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains UI presentation callables for the CLI app."""

from functools import partial

from rich.console import Console
from rich.panel import Panel


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
