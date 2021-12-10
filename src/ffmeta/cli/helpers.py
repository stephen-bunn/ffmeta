# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains helpers for various CLI apps.

These services are intended to be called within commands.
They can potentially raise `typer.Exit` exceptions to shortcircuit the running command.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ffmeta.services import write_metadata
from ffmeta.types import MediaMetadata

from .prompt import prompt_confirm, prompt_media_chapters, prompt_media_tags
from .ui import display_error, display_success, status


def edit_metadata_tags(
    console: Console,
    media_filepath: Path,
    metadata: MediaMetadata,
) -> MediaMetadata:
    """Edit some given metadata tags.

    Args:
        console (~rich.console.Console):
            The console to use for rendering
        media_filepath (~pathlib.Path):
            The filepath of the media the metadata belongs to
        metadata (~ffmeta.types.MediaMetadata):
            The metadata to edit the tags of

    Returns:
        ~ffmeta.types.MediaMetadata:
            A new metadata instance using the edited tags
    """

    return MediaMetadata(
        version=metadata.version,
        tags=[
            (definition.key, value)
            for definition, value in prompt_media_tags(
                console, media_filepath, metadata
            )
        ],
        chapters=metadata.chapters,
    )


def edit_metadata_chapters(
    console: Console,
    media_filepath: Path,
    metadata: MediaMetadata,
) -> MediaMetadata:
    """Edit some given metadata chapters.

    Args:
        console (~rich.console.Console):
            The console to use for rendering
        media_filepath (~pathlib.Path):
            The filepath of the media the metadata belongs to
        metadata (~ffmeta.types.MediaMetadata):
            The metadata to edit the chapters of

    Returns:
        ~ffmeta.types.MediaMetadata:
            A new metadata instance using the edited chapters
    """

    return MediaMetadata(
        version=metadata.version,
        tags=metadata.tags,
        chapters=prompt_media_chapters(console, media_filepath, metadata),
    )


def apply_metadata(
    console: Console,
    media_filepath: Path,
    metadata: MediaMetadata,
    output_filepath: Optional[Path] = None,
    overwrite: bool = False,
):
    """Apply some given metadata to some media.

    Args:
        console (~rich.console.Console):
            The console to use for rendering
        media_filepath (~pathlib.Path):
            The filepath of the media the metadata belongs to
        metadata (~ffmeta.types.MediaMetadata):
            The metadata to edit the tags of
        output_filepath (~pathlib.Path):
            The filepath of the media to create with the existing metadata
            Defaults to None.
        overwrite (bool):
            If true, will allow for existing output filepaths to be overwritten
            Defaults to False.
    """

    out = (
        output_filepath
        if output_filepath
        else media_filepath.with_suffix(f".ffmeta{media_filepath.suffix}")
    )

    if not prompt_confirm(console, f"\nWrite metadata to [bold green]{out}[/]?"):
        display_error(console, "User aborted writing metadata")
        raise typer.Exit(0)

    with status(console, f"Writing metadata to [bold green]{out}[/bold green]..."):
        write_metadata(metadata, media_filepath, out, overwrite=overwrite)

    display_success(
        console,
        f"Successfully wrote chapters to [bold white]{out.absolute()}[/bold white]!",
    )
