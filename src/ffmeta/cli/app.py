# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the main CLI app."""

import warnings
from pathlib import Path

import typer

from ffmeta.serialize import dumps_metadata, load_metadata
from ffmeta.services import probe_metadata

from .ui import build_tags_renderable, display_error
from .utils import get_console

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@app.callback()
def main(
    ctx: typer.Context,
    color: bool = typer.Option(default=True, help="Enable color output."),
    warn: bool = typer.Option(default=False, help="Enable warnings output."),
):
    """FFMeta.

    FFMpeg-based media metadata utility.
    """

    if not warn:
        warnings.simplefilter("ignore")


@app.command("probe")
def probe(ctx: typer.Context, media_filepath: Path = typer.Argument(...)):
    """Probe some media file for existing metadata."""

    console = get_console(ctx)
    if not media_filepath.is_file():
        display_error(
            console,
            f"Media at [white]{media_filepath}[/white] doesn't exist",
        )
        raise typer.Exit(1)

    console.print_json(dumps_metadata(probe_metadata(media_filepath)))


@app.command("show")
def show(ctx: typer.Context, metadata_filepath: Path = typer.Argument(...)):
    """Show some metadata from a given metadata file."""

    console = get_console(ctx)
    if not metadata_filepath.is_file():
        display_error(
            console,
            f"Metadata at [white]{metadata_filepath}[/white] doesn't exist",
        )
        raise typer.Exit(1)

    with metadata_filepath.open("r") as metadata_io:
        metadata = load_metadata(metadata_io)
        console.print(build_tags_renderable(metadata.tags))
