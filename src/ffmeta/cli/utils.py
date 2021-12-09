# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains generic helpers that the CLI needs to isolate."""

from functools import partial
from pathlib import Path
from typing import Any, Callable

import typer
from rich.console import Console

from ffmeta.utils import noop

from .ui import display_error


def _get_root_context(ctx: typer.Context) -> typer.Context:
    """Get the very root context instance.

    Args:
        ctx (~typer.Context):
            The provided (potentially nested) context instance.

    Returns:
        ~typer.Context:
            The root context instance.
    """

    if ctx.parent is None:
        return ctx

    context = ctx.parent
    while hasattr(context, "parent") and context.parent is not None:
        context = context.parent

    # this is "technically" a click Context
    return context  # type: ignore


def is_debug_context(ctx: typer.Context) -> bool:
    """Determine if the current context is marked for extra debugging.

    Args:
        ctx (~typer.Context):
            The current commands context instance.

    Returns:
        bool:
            True if the context is marked for debug output, otherwise False.
    """

    context = _get_root_context(ctx)
    return context.params.get("debug", False)


def get_console(ctx: typer.Context) -> Console:
    """Get a rich Console instance given the context.

    Args:
        ctx (~typer.Context):
            The current typer context instance.

    Returns:
        ~rich.console.Console: The appropriate console instance given the context.
    """

    context = _get_root_context(ctx)
    is_color = context.params.get("color", True)

    return Console(
        color_system=("auto" if is_color else None),
    )


def get_echo(ctx: typer.Context) -> Callable[[str], Any]:
    """Get the appropriate print callable given the context.

    Args:
        ctx (~typer.Context):
            The current typer context instance.

    Returns:
        Callable[[str], Any]: The appropriate print callable given the context.
    """

    if is_debug_context(ctx):
        return noop

    console = get_console(ctx)
    return partial(console.print)


def ensure_path_exists(console: Console, path: Path):
    """Ensure that a given path exists before continuing.

    Displays an error panel and exits the app if the path doesn't exit.

    Args:
        console (rich.Console):
            The console to use to display the error
        path (pathlib.Path):
            The path to validate exists

    Raises:
        typer.Exit:
            If the given path does not exist
    """

    if path.exists():
        return

    display_error(console, f"File at [white]{path}[/white] does not exist!")
    raise typer.Exit(1)
