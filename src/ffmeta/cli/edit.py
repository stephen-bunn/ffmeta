# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the `edit` CLI app."""

from pathlib import Path
from typing import Optional

import typer

from ffmeta.cli.utils import get_console
from ffmeta.services import probe_metadata

from .helpers import apply_metadata, edit_metadata_chapters, edit_metadata_tags
from .prompt import prompt_media_chapter
from .ui import display_error
from .utils import ensure_path_exists

edit_app = typer.Typer(
    name="edit",
    help="Subcommand for editing existing metadata files",
)


@edit_app.command("tags")
def edit_tags(
    ctx: typer.Context,
    media: Path = typer.Argument(...),
    out: Optional[Path] = typer.Option(None, "-o", "--out"),
    overwrite: bool = typer.Option(False),
):
    """Edit only the tags of some given media."""

    console = get_console(ctx)
    ensure_path_exists(console, media)

    metadata = probe_metadata(media)
    metadata = edit_metadata_tags(console, media, metadata)

    apply_metadata(console, media, metadata, output_filepath=out, overwrite=overwrite)


@edit_app.command("chapters")
def edit_chapters(
    ctx: typer.Context,
    media: Path = typer.Argument(...),
    chapter: Optional[int] = typer.Option(None, "-c", "--chapter"),
    out: Optional[Path] = typer.Option(None, "-o", "--out"),
    overwrite: bool = typer.Option(False),
):
    """Edit only chapters of some given media."""

    console = get_console(ctx)
    ensure_path_exists(console, media)

    metadata = probe_metadata(media)
    if chapter:
        if chapter < 0 or chapter >= len(metadata.chapters):
            display_error(
                console,
                f"Chapter at index [white]{chapter}[/white] does not exist in "
                f"[white]{media}[/white]",
            )
            raise typer.Exit(1)

        metadata.chapters.insert(
            chapter,
            prompt_media_chapter(
                console,
                media,
                current_chapter=metadata.chapters[chapter],
                previous_chapters=metadata.chapters[:chapter],
                next_chapters=metadata.chapters[chapter + 1 :],
            ),
        )
    else:
        metadata = edit_metadata_chapters(console, media, metadata)

    apply_metadata(console, media, metadata, output_filepath=out, overwrite=overwrite)


@edit_app.command("all")
def edit_all(
    ctx: typer.Context,
    media: Path = typer.Argument(...),
    out: Optional[Path] = typer.Option(None, "-o", "--out"),
    overwrite: bool = typer.Option(False),
):
    """Edit all metadata for some given media."""

    console = get_console(ctx)
    ensure_path_exists(console, media)

    metadata = probe_metadata(media)
    metadata = edit_metadata_tags(console, media, metadata)
    metadata = edit_metadata_chapters(console, media, metadata)

    apply_metadata(console, media, metadata, output_filepath=out, overwrite=overwrite)
